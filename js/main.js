document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const statusMessage = document.getElementById('statusMessage');
    const studentInfo = document.getElementById('studentInfo');
    
    // 按钮
    const captureBtn = document.getElementById('captureBtn');
    const trainBtn = document.getElementById('trainBtn');
    const recognizeBtn = document.getElementById('recognizeBtn');
    const exportBtn = document.getElementById('exportBtn');
    const preprocessBtn = document.getElementById('preprocessBtn');
    const trainTorchBtn = document.getElementById('trainTorchBtn');
    const predictBtn = document.getElementById('predictBtn');
    const generateTableBtn = document.getElementById('generateTableBtn');
    
    // 启动摄像头
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function(stream) {
                video.srcObject = stream;
            })
            .catch(function(error) {
                showStatus('无法访问摄像头: ' + error.message, 'error');
            });
    } else {
        showStatus('您的浏览器不支持摄像头访问', 'error');
    }
    
    // 采集人脸
    captureBtn.addEventListener('click', function() {
        const studentId = prompt('请输入学号:');
        const studentName = prompt('请输入姓名:');
        
        if (studentId && studentName) {
            captureFace(studentId, studentName);
        }
    });
    
    // 训练模型
    trainBtn.addEventListener('click', trainModel);
    
    // 识别签到
    recognizeBtn.addEventListener('click', recognizeFace);
    
    // 导出签到表
    exportBtn.addEventListener('click', exportAttendance);

    // 数据预处理
    preprocessBtn.addEventListener('click', dataPreprocess);

    // 训练模型(torch)
    trainTorchBtn.addEventListener('click', trainModelTorch);

    // 人脸检测
    predictBtn.addEventListener('click', facePredict);

    // 生成表格
    generateTableBtn.addEventListener('click', generateTable);
    
    function captureFace(studentId, studentName) {
        // 从视频中捕获一帧
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/jpeg');
        
        // 发送到后端
        fetch('http://localhost:5000/capture', {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ studentId, studentName, image: imageData })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showStatus(`成功采集 ${studentName} 的人脸数据`, 'success');
            } else {
                showStatus(data.message || '采集失败', 'error');
            }
        })
        .catch(error => {
            showStatus('请求失败: ' + error.message, 'error');
        });
    }
    
    async function trainModel() {
        const statusEl = document.getElementById('train-status');
        if (statusEl) {
            statusEl.textContent = "训练中...";
        } else {
            console.error("找不到状态显示元素");
        }
        statusEl.className = "status-pending";
        
        try {
            const response = await fetch('http://localhost:5000/train', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP错误: ${response.status}`);
            }
            
            const data = await response.json();
            if (data.success) {
                statusEl.textContent = "✅ 训练成功";
                statusEl.className = "status-success";
            } else {
                throw new Error(data.message || "训练失败");
            }
        } catch (error) {
            statusEl.textContent = `❌ 错误: ${error.message}`;
            statusEl.className = "status-error";
            console.error("训练错误:", error);
        }
    }
    
    function recognizeFace() {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/jpeg');
        
        fetch('http://localhost:5000/recognize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image: imageData
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showStatus('签到成功', 'success');
                studentInfo.innerHTML = `
                    <p><strong>姓名:</strong> ${data.studentName}</p>
                    <p><strong>学号:</strong> ${data.studentId}</p>
                    <p><strong>时间:</strong> ${new Date().toLocaleString()}</p>
                `;
            } else {
                showStatus(data.message || '识别失败', 'error');
                studentInfo.innerHTML = '';
            }
        })
        .catch(error => {
            showStatus('请求失败: ' + error.message, 'error');
            console.error('Error:', error);
        });
    }
    
    function exportAttendance() {
        fetch('http://localhost:5000/export', {
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = '签到表.xlsx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            showStatus('导出失败: ' + error.message, 'error');
        });
    }

    function dataPreprocess() {
        fetch('http://localhost:5000/preprocess', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showStatus('数据预处理成功', 'success');
            } else {
                showStatus(data.message || '数据预处理失败', 'error');
            }
        })
        .catch(error => {
            showStatus('请求失败: ' + error.message, 'error');
        });
    }

    async function trainModelTorch() {
        const statusEl = document.getElementById('train-status');
        if (statusEl) {
            statusEl.textContent = "使用torch训练中...";
        } else {
            console.error("找不到状态显示元素");
        }
        statusEl.className = "status-pending";
        
        try {
            const response = await fetch('http://localhost:5000/train_torch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP错误: ${response.status}`);
            }
            
            const data = await response.json();
            if (data.success) {
                statusEl.textContent = "✅ 使用torch训练成功";
                statusEl.className = "status-success";
            } else {
                throw new Error(data.message || "使用torch训练失败");
            }
        } catch (error) {
            statusEl.textContent = `❌ 错误: ${error.message}`;
            statusEl.className = "status-error";
            console.error("使用torch训练错误:", error);
        }
    }

    function facePredict() {
        fetch('http://localhost:5000/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showStatus('人脸检测成功', 'success');
            } else {
                showStatus(data.message || '人脸检测失败', 'error');
            }
        })
        .catch(error => {
            showStatus('请求失败: ' + error.message, 'error');
        });
    }

    function generateTable() {
        fetch('http://localhost:5000/generate_table', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showStatus('表格生成成功', 'success');
            } else {
                showStatus(data.message || '表格生成失败', 'error');
            }
        })
        .catch(error => {
            showStatus('请求失败: ' + error.message, 'error');
        });
    }
    
    function showStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = type;
    }
});