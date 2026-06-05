import torch
import numpy as np
import cv2
from PIL import Image
import albumentations as A
from albumentations.pytorch import ToTensorV2

def generate_gradcam(model, image_path: str, class_idx: int, device) -> np.ndarray:
    model.eval()

    # Load image
    image = np.array(Image.open(image_path).convert('RGB'))
    transform = A.Compose([
        A.Resize(300, 300),
        A.CenterCrop(260, 260),
        A.Normalize(mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]),
        ToTensorV2()
    ])
    tensor = transform(image=image)['image'].unsqueeze(0).to(device)

    # Hook to capture gradients and activations
    gradients  = []
    activations = []

    def backward_hook(module, grad_input, grad_output):
        gradients.append(grad_output[0])

    def forward_hook(module, input, output):
        activations.append(output)

    # Register hooks on last conv layer
    target_layer = model.backbone.blocks[-1]
    fh = target_layer.register_forward_hook(forward_hook)
    bh = target_layer.register_backward_hook(backward_hook)

    # Forward pass
    output = model(tensor)
    model.zero_grad()
    output[0, class_idx].backward()

    # Remove hooks
    fh.remove()
    bh.remove()

    # Generate CAM
    grad    = gradients[0].cpu().detach().numpy()[0]
    act     = activations[0].cpu().detach().numpy()[0]
    weights = grad.mean(axis=(1, 2))
    cam     = np.zeros(act.shape[1:], dtype=np.float32)

    for i, w in enumerate(weights):
        cam += w * act[i]

    cam = np.maximum(cam, 0)
    cam = cv2.resize(cam, (260, 260))

    if cam.max() > 0:
        cam = (cam - cam.min()) / (cam.max() - cam.min())

    # Overlay on original image
    original = cv2.resize(
        np.array(Image.open(image_path).convert('RGB')),
        (260, 260)
    )
    heatmap  = cv2.applyColorMap(
        np.uint8(255 * cam), cv2.COLORMAP_JET
    )
    heatmap  = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    overlay  = cv2.addWeighted(original, 0.6, heatmap, 0.4, 0)

    return overlay, cam