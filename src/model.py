import torch.nn as nn
import timm

class PlantDiseaseClassifier(nn.Module):
    def __init__(self, num_classes=38, pretrained=False):
        super().__init__()
        self.backbone = timm.create_model(
            'efficientnet_b3',
            pretrained=pretrained,
            num_classes=0
        )
        in_features = self.backbone.num_features
        self.classifier = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(in_features, 512),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        features = self.backbone(x)
        return self.classifier(features)