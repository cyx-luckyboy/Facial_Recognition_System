import cv2
import time
import xlrd
import xlwt
from xlutils.copy import copy
from datetime import datetime

# 假设这里可以导入 app.py 中的 attendance_records 列表
from app import attendance_records

# 创建签名子函数
def sign_in(idx, name, student_id):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    attendance_record = {
        '学号': student_id,
        '姓名': name,
        '签到时间': timestamp
    }
    attendance_records.append(attendance_record)

    # 以下是原有的写入 Excel 文件逻辑，可根据需要保留或删除
    style0 = xlwt.easyxf('font:height 300,bold on,color_index black', num_format_str='MM:DD HH:MM')
    style1 = xlwt.easyxf('font:height 300,bold on,color_index blue', num_format_str='MM:DD HH:MM')
    wb = xlrd.open_workbook('人脸识别excel.xls')
    nwb = copy(wb)
    nbs = nwb.get_sheet(0)
    # 签名
    nbs.write(idx, 3, name, style1)
    # 签时间
    nbs.write(idx, 4, datetime.now(), style0)
    nbs.col(4).width = 256 * 20
    nwb.save('人脸识别excel.xls')

# 加载模型
classfier = cv2.CascadeClassifier('E:\pythonProject\pythonProject2\haarcascade_frontalface_default.xml')
create = cv2.face_LBPHFaceRecognizer.create()
create.read('trainer.yml')

# 定义变量
font = cv2.FONT_ITALIC
starttime = time.time()
ID = ('UNKNOWN')
name = ('UNKNOWN')
count = 0

# 从表格中获取学号、姓名，与识别结果比对
workbook = xlrd.open_workbook('人脸识别excel.xls')
worksheet = workbook.sheet_by_index(0)
stu_id = worksheet.col_values(1)
stu_name = worksheet.col_values(2)
print(stu_id)
print(stu_name)

# 打开摄像头
capture = cv2.VideoCapture(0)
while capture.isOpened():
    kk = cv2.waitKey(1)
    _, farme = capture.read()
    gray = cv2.cvtColor(farme, cv2.COLOR_BGR2GRAY)
    faces = classfier.detectMultiScale(gray, 1.2, 5)
    if len(faces) != 0:
        for x, y, w, h in faces:
            cv2.rectangle(farme, (x, y), (x + w, y + h), (180, 120, 220), 2)
            gray1 = gray[y:y + h, x:x + w]
            label, conf = create.predict(gray1)
            print(label, conf)
            if conf < 50:
                index = [i for i, id in enumerate(stu_id) if str(id) == str(label)]
                if index:  # 检查 index 列表是否为空
                    ID = str(label)
                    name = stu_name[index[0]]
                    print(ID, name)
                    count = count + 1
                else:
                    ID = 'UNKNOWN'
                    name = 'UNKNOWN'
            else:
                ID = 'UNKNOWN'
                name = 'UNKNOWN'
            cv2.putText(farme, str(ID), (x + w // 2 - 50, y + h + 30), font, 1.2, (200, 0, 250), 2)

    cv2.putText(farme, 'Press "q" to quit', (30, 60), font, 1.2, (200, 0, 250), 2)
    cv2.imshow('picture from capture.', farme)
    if kk == ord('q'):
        break

    if count > 30 and name != 'UNKNOWN':
        sign_in(index[0], name, ID)
        print('学号为：' + str(label) + ',姓名为：' + str(name))
        break

    if time.time() - starttime > 30:
        print('超时未识别')
        break

# 关闭所有窗口，释放摄像头
capture.release()
cv2.destroyAllWindows()