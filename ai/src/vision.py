import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import io
import os
from src.model import create_model

class VisionEngine:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f" Göz Motoru Başlatılıyor... (Cihaz: {self.device})")
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, "..", "data", "raw")
        self.class_names = sorted(os.listdir(data_dir))
        num_classes = len(self.class_names)
        
        self.model = create_model(num_classes=num_classes)
        model_path = os.path.join(current_dir, "..", "models", "efficientnet_b0_finetuned.pt")
        self.model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
        
        self.model.to(self.device)
        self.model.eval() 
        
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        print(f" Göz Motoru Hazır! Öğrenilen Sınıflar: {self.class_names}")

    def predict(self, image_bytes):
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = F.softmax(outputs, dim=1)[0]
                confidence, predicted_idx = torch.max(probabilities, 0)

            food_name = self.class_names[predicted_idx.item()]
            return {"food": food_name, "confidence": confidence.item()}
        except Exception as e:
            print(f" Görüntü işleme hatası: {e}")
            return None