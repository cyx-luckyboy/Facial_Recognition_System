import cv2
import numpy as np
from PIL import Image
import os

create = cv2.face.LBPHFaceRecognizer_create()

def data_translate(path):
    face_data = []
    id_data = []
    file_list = [os.path.join(path, f) for f in os.listdir(path)]
    # print(file_list)
    # print(len(file_list))
    for file in file_list:
        PIL_image = Image.open(file).convert('L')
        np_image = np.array(PIL_image, "uint8")
        # print(file)
        # print(file.split('.'))
        # print(file.split('.')[1])
        id = int(file.split('.')[1])
        # print(file.split('.')[0])
        face_data.append(np_image)
        id_data.append(id)
    return face_data, id_data

print('开始训练模型')

# data_translate(r'data\data')
Faces,Ids = data_translate(r'E:\pythonProject\pythonProject2\data')

create.train(Faces,np.array((Ids)))

create.save('trainer.yml')
print('模型保存成功')
