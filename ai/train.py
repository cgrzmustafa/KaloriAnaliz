import os
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from tqdm import tqdm
from src.dataloader import create_dataloaders
from src.model import create_model

def train_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f" Eğitim şu cihazda başlıyor: {device}")

    data_dir = "data/raw"
    train_loader, val_loader, test_loader, classes = create_dataloaders(data_dir, batch_size=32)

    num_classes = len(classes)
    model = create_model(num_classes=num_classes).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-4, weight_decay=1e-4)

    num_epochs = 3 
    
    train_losses, val_losses = [], []
    train_accs, val_accs = [], []

    print("\n Eğitim Döngüsü Başlıyor...")
    for epoch in range(num_epochs):
        model.train()
        running_loss, correct, total = 0.0, 0, 0
        
        loop = tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs} [Train]", leave=False)
        for images, labels in loop:
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
            
            loop.set_postfix(loss=loss.item(), acc=100.*correct/total)

        train_losses.append(running_loss / len(train_loader))
        train_accs.append(100. * correct / total)

        model.eval()
        val_loss, correct, total = 0.0, 0, 0
        with torch.no_grad():
            loop = tqdm(val_loader, desc=f"Epoch {epoch+1}/{num_epochs} [Val]", leave=False)
            for images, labels in loop:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()

        val_losses.append(val_loss / len(val_loader))
        val_accs.append(100. * correct / total)
        
        print(f"Epoch {epoch+1}/{num_epochs} | Train Loss: {train_losses[-1]:.4f} | Train Acc: {train_accs[-1]:.2f}% | Val Loss: {val_losses[-1]:.4f} | Val Acc: {val_accs[-1]:.2f}%")

    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), "models/efficientnet_b0_finetuned.pt")
    print("\n Model ağırlıkları 'models/efficientnet_b0_finetuned.pt' konumuna kaydedildi.")

    os.makedirs("../docs", exist_ok=True) 
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label='Train Loss', color='blue')
    plt.plot(val_losses, label='Val Loss', color='orange')
    plt.legend()
    plt.title("Loss Eğrisi")

    plt.subplot(1, 2, 2)
    plt.plot(train_accs, label='Train Accuracy', color='green')
    plt.plot(val_accs, label='Val Accuracy', color='red')
    plt.legend()
    plt.title("Accuracy Eğrisi")

    plt.savefig("../docs/training_metrics.png")
    print(" Eğitim grafikleri '../docs/training_metrics.png' konumuna kaydedildi.")

if __name__ == "__main__":
    train_model()