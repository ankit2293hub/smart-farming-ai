import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from src.model import PlantDiseaseClassifier
from src.dataset import PlantDataset, train_transforms, val_transforms

def train_model():
    # Device
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}")

    # Datasets
    train_dataset = PlantDataset('data/processed/train', transform=train_transforms)
    val_dataset   = PlantDataset('data/processed/val',   transform=val_transforms)

    train_loader = DataLoader(train_dataset, batch_size=32,
                              shuffle=True, num_workers=2, pin_memory=False)
    val_loader   = DataLoader(val_dataset,   batch_size=32,
                              shuffle=False, num_workers=2, pin_memory=False)

    print(f"Train: {len(train_dataset)} | Val: {len(val_dataset)}")

    # Model
    model = PlantDiseaseClassifier(num_classes=38).to(device)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

    # STAGE 1 — Freeze backbone, train head only (3 epochs)
    print("\n=== Stage 1: Training classifier head ===")
    model.freeze_backbone()
    optimizer = AdamW(model.classifier.parameters(), lr=1e-3)

    for epoch in range(3):
        model.train()
        total, correct, running_loss = 0, 0, 0

        for i, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

            if i % 50 == 0:
                print(f"  Epoch {epoch+1} | Step {i}/{len(train_loader)} "
                      f"| Loss: {running_loss/(i+1):.3f} "
                      f"| Acc: {100.*correct/total:.1f}%")

        # Validation
        val_acc = evaluate(model, val_loader, device)
        print(f"  ✅ Epoch {epoch+1} Val Accuracy: {val_acc:.1f}%")

    # STAGE 2 — Unfreeze all, fine-tune (7 epochs)
    print("\n=== Stage 2: Fine-tuning full model ===")
    model.unfreeze_all()
    optimizer = AdamW(model.parameters(), lr=1e-4, weight_decay=1e-5)
    scheduler = CosineAnnealingLR(optimizer, T_max=7)

    best_val_acc = 0
    os.makedirs('models', exist_ok=True)

    for epoch in range(7):
        model.train()
        total, correct, running_loss = 0, 0, 0

        for i, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

            if i % 50 == 0:
                print(f"  Epoch {epoch+1} | Step {i}/{len(train_loader)} "
                      f"| Loss: {running_loss/(i+1):.3f} "
                      f"| Acc: {100.*correct/total:.1f}%")

        val_acc = evaluate(model, val_loader, device)
        scheduler.step()
        print(f"  ✅ Epoch {epoch+1} Val Accuracy: {val_acc:.1f}%")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                'model_state_dict': model.state_dict(),
                'val_acc': val_acc,
                'classes': train_dataset.classes
            }, 'models/best_model.pth')
            print(f"  💾 Saved best model! Val Acc: {val_acc:.1f}%")

    print(f"\n🎉 Training complete! Best val accuracy: {best_val_acc:.1f}%")

def evaluate(model, loader, device):
    model.eval()
    total, correct = 0, 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
    return 100. * correct / total

if __name__ == '__main__':
    train_model()