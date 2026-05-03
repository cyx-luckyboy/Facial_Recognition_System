import cv2
import os

# 定义变量
classifier = cv2.CascadeClassifier(r'E:\pythonProject\pythonProject2\haarcascade_frontalface_default.xml')
font = cv2.FONT_HERSHEY_SIMPLEX
stu_id = input('请输入你的学号： \n')
stu_name = input('请输入你的姓名： \n')
count = 0

# 建立人脸数据文件夹
if not os.path.exists('data'):
    os.mkdir('data')

# 打开摄像头
capture = cv2.VideoCapture(0)

while capture.isOpened():
    kk = cv2.waitKey(1)
    _,farme = capture.read()

    gray = cv2.cvtColor(farme, cv2.COLOR_BGR2GRAY)
    faces = classifier.detectMultiScale(gray, 1.2, 5)

    if len(faces) != 0:
        for x, y, w, h in faces:
            cv2.rectangle(farme, (x, y), (x + w, y + h), (200, 0, 250), 2)
            # center = (x + w // 2, y + h // 2)
            # r = w // 2
            # cv2.circle(farme, center, r, (0, 250, 0), 2)
            cv2.putText(farme, 'Press "s" to save' , (x + w, y + h), font, 1, (200, 0, 250), 2)

            if kk == ord('s'):
                cv2.imwrite('data/'+str(stu_name)+'.'+str(stu_id)+'.'+str(count)+'.jpg', gray[y:y+h,x:x+w])
                count += 1
                print('采集了'+str(count)+'张图片。')

    cv2.putText(farme, 'Press "q" to quit', (30, 60), font, 1, (200, 0, 250), 2)
    cv2.imshow('Picture from capture',farme)

    if kk == ord('q'):
        print('共采集了学号为'+str(stu_id)+'姓名为'+str(stu_name)+'的同学的'+str(count)+'张图片')
        break

# 释放摄像头
capture.release()
cv2.destroyAllWindows()

