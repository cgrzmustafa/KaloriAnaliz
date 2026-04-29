import torch
import torch.nn as nn
from efficientnet_pytorch import EfficientNet

def create_model(num_classes):
    model = EfficientNet.from_pretrained('efficientnet-b0')

    for param in model.parameters():
        param.requires_grad = False

    for block in model._blocks[-2:]:
        for param in block.parameters():
            param.requires_grad = True

    for param in model._conv_head.parameters():
        param.requires_grad = True
    for param in model._bn1.parameters():
        param.requires_grad = True

    in_features = model._fc.in_features
    model._fc = nn.Sequential(
        nn.Dropout(p=0.2), 
        nn.Linear(in_features, num_classes)
    )

    return model

if __name__ == "__main__":
    temp_model = create_model(num_classes=161)
    print("✅ Model başarıyla oluşturuldu!")
    
    trainable_params = sum(p.numel() for p in temp_model.parameters() if p.requires_grad)
    print(f"Eğitilebilir parametre sayısı: {trainable_params:,}")