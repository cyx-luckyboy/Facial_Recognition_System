# 导入库
import tkinter as tk
import os
from PIL import Image, ImageTk
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime  # 用于获取签到时间


def send_email(to_email, student_name, student_id):
    smtp_server = "smtp.qq.com"
    smtp_port = 465
    sender_email = "1246675664@qq.com"
    sender_password = "zwhocnicnjgpjaig"  # 必须是授权码！

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = f"签到成功通知 - {student_name}"
    msg.attach(MIMEText(f"姓名：{student_name}\n学号：{student_id}", "plain"))

    try:
        # 方案1：使用 SMTP_SSL（推荐）
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        print("邮件发送成功！")
        return True

    except smtplib.SMTPAuthenticationError:
        print("错误：邮箱认证失败，请检查账号/授权码")
    except Exception as e:
        print(f"邮件发送失败：{e}")
        # 方案2：尝试 starttls（备用）
        try:
            server = smtplib.SMTP(smtp_server, 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            print("邮件发送成功（通过TLS）！")
            return True
        except Exception as e2:
            print(f"备用方案也失败：{e2}")
    return False


# 创建采集人脸子函数
def CJRL():
    os.system('python 采集人脸.py')


# 创建训练模型子函数
def XL():
    os.system('python 训练模型.py')


# 创建识别签到子函数
def SBQD():
    os.system('python 识别签到.py')

    # 假设签到后获取学生信息
    student_id = "1111111111"  # 实际应从人脸识别结果获取
    student_name = "cyx"  # 实际应从Excel或数据库获取
    student_email = "1246675664@qq.com"  # 需要提前存储学生邮箱

    send_email(student_email, student_name, student_id)


# 创建签到表
def QDB():
    os.startfile('人脸识别excel.xls')


# 关闭窗口
def GB():
    win.destroy()


# 数据预处理
def data_preprocess():
    os.system('python _data_preprocess.py')


# 训练模型（使用torch）
def train_model_torch():
    os.system('python _train_model.py')


# 人脸预测
def face_predict():
    os.system('python _face_predict.py')


# 生成表格
def generate_table():
    os.system('python 生成表格.py')


# 创建窗口
win = tk.Tk()
win.title('人脸识别签到系统')
win.geometry('310x700+800+50')
win.configure(bg='pink')

# 创建一个主框架用于居中内容
main_frame = tk.Frame(win, bg='pink')
main_frame.pack(expand=True)  # 使用pack布局并允许扩展

# 设置图片以便使用
img = Image.open('E:\\pythonProject\\pythonProject2\\cyx1.jpg')
photo = ImageTk.PhotoImage(img)

# 大标题 - 使用grid布局但在框架中居中
title_frame = tk.Frame(main_frame, bg='pink')
title_frame.pack(pady=10)

lab1 = tk.Label(title_frame, text="人脸识别签到系统", font=('黑体', 20, 'bold'), bg='#00BFFF', fg='white')
lab1.pack()

# 按钮框架 - 使用grid布局但在框架中居中
button_frame = tk.Frame(main_frame, bg='pink')
button_frame.pack(pady=20)

# 使用grid布局使按钮在框架中居中
but1 = tk.Button(button_frame, text='采 集 人 脸 图 片', activebackground='red', command=CJRL,
                 font=('黑体', 10, 'bold'), bg='#00BFFF', fg='white', width=20)
but1.grid(row=0, column=0, padx=20, pady=10, sticky='ew')

but2 = tk.Button(button_frame, text='训 练 模 型', activebackground='red', command=XL,
                 font=('黑体', 10, 'bold'), bg='#00BFFF', fg='white', width=20)
but2.grid(row=1, column=0, padx=20, pady=10, sticky='ew')

but3 = tk.Button(button_frame, text='识 别 签 到', activebackground='red', command=SBQD,
                 font=('黑体', 10, 'bold'), bg='#00BFFF', fg='white', width=20)
but3.grid(row=2, column=0, padx=20, pady=10, sticky='ew')

but4 = tk.Button(button_frame, text='签 到 表', activebackground='red', command=QDB,
                 font=('黑体', 10, 'bold'), bg='#00BFFF', fg='white', width=20)
but4.grid(row=3, column=0, padx=20, pady=10, sticky='ew')

but5 = tk.Button(button_frame, text='数 据 预 处 理', activebackground='red', command=data_preprocess,
                 font=('黑体', 10, 'bold'), bg='#00BFFF', fg='white', width=20)
but5.grid(row=4, column=0, padx=20, pady=10, sticky='ew')

but6 = tk.Button(button_frame, text='训 练 模 型(torch)', activebackground='red', command=train_model_torch,
                 font=('黑体', 10, 'bold'), bg='#00BFFF', fg='white', width=20)
but6.grid(row=5, column=0, padx=20, pady=10, sticky='ew')

but7 = tk.Button(button_frame, text='人 脸 检 测', activebackground='red', command=face_predict,
                 font=('黑体', 10, 'bold'), bg='#00BFFF', fg='white', width=20)
but7.grid(row=6, column=0, padx=20, pady=10, sticky='ew')

but8 = tk.Button(button_frame, text='关 闭 窗 口', activebackground='red', command=GB,
                 font=('黑体', 10, 'bold'), bg='#00BFFF', fg='white', width=20)
but8.grid(row=7, column=0, padx=20, pady=10, sticky='ew')

# 配置按钮框架的列权重
button_frame.grid_columnconfigure(0, weight=1)

win.mainloop()