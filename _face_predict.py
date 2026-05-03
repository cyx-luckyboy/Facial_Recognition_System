import os
import torch
import cv2
import numpy as np
from torchvision import transforms
from PIL import Image, ImageFont, ImageDraw
from facenet_pytorch import MTCNN
from torchvision import models
import torch.nn as nn
import tkinter as tk
from tkinter import filedialog

# ---------------- 配置参数 ----------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_path = 'saved_finetuned_model.pth'
class_names = os.listdir('processed_faces')
input_size = 120
confidence_threshold = 0.80  # 设置阈值

# ---------------- 初始化人脸检测器 MTCNN ----------------
mtcnn = MTCNN(image_size=input_size, margin=20, keep_all=True, device=device)

# ---------------- 图像预处理 ----------------
transform = transforms.Compose([
    transforms.Resize((input_size, input_size)),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])

# ---------------- 加载模型 ----------------
model = models.mobilenet_v2(pretrained=False)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(class_names))
model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()
model = model.to(device)

def select_image():
    # 打开文件选择对话框
    file_path = filedialog.askopenfilename()
    if file_path:
        # ---------------- 加载图像 ----------------
        img_cv = cv2.imread(file_path)
        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        draw = ImageDraw.Draw(img_pil)
        font = ImageFont.truetype("simhei.ttf", 24)  # 用于显示中文

        # ---------------- 检测人脸 ----------------
        boxes, probs = mtcnn.detect(img_rgb)

        if boxes is None:
            print("❌ 未检测到人脸")
            return

        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            face = img_rgb[y1:y2, x1:x2]
            face_pil = Image.fromarray(face)
            face_tensor = transform(face_pil).unsqueeze(0).to(device)

            # 预测
            with torch.no_grad():
                outputs = model(face_tensor)
                prob_tensor = torch.nn.functional.softmax(outputs, dim=1)
                confidence, pred = torch.max(prob_tensor, 1)

            conf_value = confidence.item()
            if conf_value >= confidence_threshold:
                name = class_names[pred.item()]
                color = (0, 255, 0)  # Green
                label = f"{name} ({conf_value*100:.1f}%)"
            else:
                name = "Unknown"
                color = (0, 0, 255)  # Red
                label = f"{name} ({conf_value*100:.1f}%)"

            # 绘制框和标签
            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
            draw.text((x1, y1 - 25), label, font=font, fill=color)

        # ---------------- 显示图像 ----------------
        result = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        cv2.imshow("Face Recognition", result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# 创建主窗口
root = tk.Tk()
root.title("人脸识别系统")

# 创建按钮
button = tk.Button(root, text="选择图片", command=select_image)
button.pack(pady=20)

# 运行主循环
root.mainloop()