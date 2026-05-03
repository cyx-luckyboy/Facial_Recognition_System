from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import cv2
import numpy as np
import base64
from datetime import datetime
import pandas as pd
import subprocess

# 确保全局变量统一
attendance_records = []
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"]
    }
})

app.config['UPLOAD_FOLDER'] = 'data'
app.config['TRAINED_MODEL'] = 'model.yml'

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化人脸识别器
recognizer = cv2.face.LBPHFaceRecognizer_create()
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 存储学生信息
students = {}
attendance = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/capture', methods=['POST'])
def capture():
    data = request.json
    student_id = data['studentId']
    student_name = data['studentName']
    image_data = data['image']

    # 解码Base64图像
    header, encoded = image_data.split(",", 1)
    binary_data = base64.b64decode(encoded)
    np_data = np.frombuffer(binary_data, dtype=np.uint8)
    image = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 检测人脸
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        return jsonify({'success': False, 'message': '未检测到人脸'})

    # 保存人脸图像
    (x, y, w, h) = faces[0]
    face_img = gray[y:y + h, x:x + w]

    # 创建学生文件夹
    student_folder = os.path.join(app.config['UPLOAD_FOLDER'], f"{student_id}_{student_name}")
    os.makedirs(student_folder, exist_ok=True)

    # 保存图像
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(student_folder, f"{timestamp}.jpg")
    cv2.imwrite(filename, face_img)

    # 记录学生信息
    students[student_id] = student_name

    return jsonify({'success': True})


@app.route('/train', methods=['OPTIONS', 'POST'])
def train_model():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    try:
        # 训练逻辑（确保data目录存在图片）
        faces = []
        labels = []

        for student_dir in os.listdir('data'):
            if '_' in student_dir:  # 格式：学号_姓名
                student_id = student_dir.split('_')[0]
                dir_path = os.path.join('data', student_dir)

                for img_file in os.listdir(dir_path):
                    if img_file.endswith('.jpg'):
                        img_path = os.path.join(dir_path, img_file)
                        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                        if img is not None:
                            faces.append(img)
                            labels.append(int(student_id))

        if not faces:
            return jsonify({"success": False, "message": "未找到训练数据"}), 400

        recognizer.train(faces, np.array(labels))
        recognizer.save('model.yml')
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/recognize', methods=['POST'])
def recognize():
    try:
        # 检查模型是否存在
        if not os.path.exists(app.config['TRAINED_MODEL']):
            return jsonify({'success': False, 'message': '请先训练模型'})

        recognizer.read(app.config['TRAINED_MODEL'])

        data = request.json
        image_data = data['image']

        # 解码Base64图像
        header, encoded = image_data.split(",", 1)
        binary_data = base64.b64decode(encoded)
        np_data = np.frombuffer(binary_data, dtype=np.uint8)
        image = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 检测人脸
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) == 0:
            return jsonify({'success': False, 'message': '未检测到人脸'})

        # 识别人脸
        (x, y, w, h) = faces[0]
        face_img = gray[y:y + h, x:x + w]

        label, confidence = recognizer.predict(face_img)

        # 如果置信度太高，可能是未知人脸
        if confidence > 80:
            return jsonify({'success': False, 'message': '未知人脸'})

        # 记录签到
        student_id = str(label)
        student_name = students.get(student_id, "未知")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        attendance_record = {
            '学号': student_id,
            '姓名': student_name,
            '签到时间': timestamp
        }
        attendance_records.append(attendance_record)  # 添加到全局变量

        return jsonify({
            'success': True,
            'studentId': student_id,
            'studentName': student_name
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/export', methods=['GET'])
def export():
    try:
        if not attendance_records:
            return jsonify({"success": False, "message": "没有签到记录"})

        # 转换为 DataFrame
        df = pd.DataFrame(attendance_records, columns=["学号", "姓名", "签到时间"])

        # 保存到临时文件
        export_path = "temp_attendance.xlsx"
        df.to_excel(export_path, index=False)

        # 发送文件
        return send_file(
            export_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='签到表.xlsx'
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/preprocess', methods=['POST'])
def data_preprocess():
    try:
        subprocess.run(['python', '_data_preprocess.py'], check=True)
        return jsonify({"success": True, "message": "数据预处理成功"})
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "message": f"数据预处理失败: {str(e)}"})


@app.route('/train_torch', methods=['POST'])
def train_model_torch():
    try:
        subprocess.run(['python', '_train_model.py'], check=True)
        return jsonify({"success": True, "message": "使用torch训练成功"})
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "message": f"使用torch训练失败: {str(e)}"})


@app.route('/predict', methods=['POST'])
def face_predict():
    try:
        subprocess.run(['python', '_face_predict.py'], check=True)
        return jsonify({"success": True, "message": "人脸检测成功"})
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "message": f"人脸检测失败: {str(e)}"})


@app.route('/generate_table', methods=['POST'])
def generate_table():
    try:
        subprocess.run(['python', '生成表格.py'], check=True)
        return jsonify({"success": True, "message": "表格生成成功"})
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "message": f"表格生成失败: {str(e)}"})


if __name__ == '__main__':
    app.run(debug=True)