import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
from tqdm import tqdm

# ---------------------  配置参数 ---------------------
data_dir = 'processed_faces'
model_save_path = 'saved_finetuned_model.pth'
num_epochs = 20
batch_size = 32
learning_rate = 1e-3
img_size = 120
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# ---------------------  数据预处理 ---------------------
data_transforms = transforms.Compose([
    transforms.Resize((img_size, img_size)),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.RandomRotation(15),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])

dataset = datasets.ImageFolder(data_dir, transform=data_transforms)
class_names = dataset.classes
num_classes = len(class_names)
print(f"Found {len(dataset)} images belonging to {num_classes} classes.")

dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

# ---------------------  构建模型 ---------------------
model = models.mobilenet_v2(pretrained=True)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
model = model.to(device)

# ---------------------  损失函数和优化器 ---------------------
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

# ---------------------  训练模型 ---------------------
best_acc = 0.0

for epoch in range(num_epochs):
    model.train()
    running_loss, running_corrects = 0.0, 0

    for inputs, labels in tqdm(dataloader, desc=f"Epoch {epoch + 1}/{num_epochs}"):
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()

        outputs = model(inputs)
        _, preds = torch.max(outputs, 1)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        running_loss += loss.item() * inputs.size(0)
        running_corrects += torch.sum(preds == labels.data)

    epoch_loss = running_loss / len(dataset)
    epoch_acc = running_corrects.double() / len(dataset)
    scheduler.step()

    print(f"Epoch {epoch+1}: Loss={epoch_loss:.4f}, Accuracy={epoch_acc:.4f}")

    # 保存最佳模型
    if epoch_acc > best_acc:
        best_acc = epoch_acc
        torch.save(model.state_dict(), model_save_path)
        print(f"✅ 最佳模型已保存，准确率：{best_acc:.4f}")

print(f"🎉 训练完成，最佳准确率为 {best_acc:.4f}，模型保存在：{model_save_path}")
