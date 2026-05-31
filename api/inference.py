import torch
import json
import numpy as np
from PIL import Image
import albumentations as A
from albumentations.pytorch import ToTensorV2
from src.model import PlantDiseaseClassifier

# Load class names
with open('models/class_names.json', 'r') as f:
    CLASS_NAMES = json.load(f)

# Device
device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')

# Load model
model = PlantDiseaseClassifier(num_classes=38, pretrained=False).to(device)
checkpoint = torch.load('models/best_model.pth', map_location=device)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

print(f"✅ Model loaded | Val Acc: {checkpoint['val_acc']:.2f}%")

# Transforms
inference_transforms = A.Compose([
    A.Resize(300, 300),
    A.CenterCrop(260, 260),
    A.Normalize(mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]),
    ToTensorV2()
])

def predict_disease(image_path: str):
    image = np.array(Image.open(image_path).convert('RGB'))
    tensor = inference_transforms(image=image)['image']
    tensor = tensor.unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(tensor)
        probs   = torch.softmax(outputs, dim=1)
        top3_probs, top3_idx = probs.topk(3, dim=1)

    disease    = CLASS_NAMES[top3_idx[0][0].item()]
    confidence = top3_probs[0][0].item()

    top3 = [
        {
            "disease"   : CLASS_NAMES[top3_idx[0][i].item()],
            "confidence": round(top3_probs[0][i].item(), 4)
        }
        for i in range(3)
    ]

    return disease, round(confidence, 4), top3