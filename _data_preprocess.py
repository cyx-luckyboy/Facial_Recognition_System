import os
from PIL import Image
from facenet_pytorch import MTCNN
from tqdm import tqdm

# 初始化 MTCNN
mtcnn = MTCNN(image_size=120, margin=20, keep_all=False)

# 原始数据路径（每个子文件夹是一个类别）
input_dir = 'known_faces'
# 输出路径
output_dir = 'processed_faces'

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 遍历每个子文件夹（类别）
for person_name in os.listdir(input_dir):
    person_folder = os.path.join(input_dir, person_name)
    if not os.path.isdir(person_folder):
        continue

    output_person_folder = os.path.join(output_dir, person_name)
    os.makedirs(output_person_folder, exist_ok=True)

    print(f"📁 正在处理: {person_name}")

    for img_name in tqdm(os.listdir(person_folder)):
        img_path = os.path.join(person_folder, img_name)

        try:
            img = Image.open(img_path).convert('RGB')  # 防止灰度图或透明图出错
            save_path = os.path.join(output_person_folder, img_name)

            face = mtcnn(img, save_path=save_path)

            if face is None:
                print(f"❌ 未检测到人脸: {img_path}")
        except Exception as e:
            print(f"⚠️ 处理出错: {img_path}，原因: {e}")
