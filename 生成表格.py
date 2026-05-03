# 引入库
import xlrd
import xlwt
from xlutils.copy import copy

# 创建工作簿
nwb = xlwt.Workbook()

cjb = nwb.add_sheet('成绩表')
cjb.write_merge(0, 0, 0, 3, '成绩表')
a = ['序号', '学号', '姓名', '成绩', '签名', '签到时间']
for i in range(6):
    cjb.write(1, i, a[i])
name = ["cyx", "陈焕贵", "李杨名", "小陈同学"]
id = ['1111111111', '2020001111', '2020002222', '2020003333']
b = 0
for a in range(2, 6):
    # 写入学号
    cjb.write(a, 1, id[b])
    # 写入姓名
    cjb.write(a, 2, name[b])
    cjb.write(a, 0, b+1)
    b = b+1
# 保存文件
nwb.save('人脸识别excel.xls')
