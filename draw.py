#导入数据处理的库
import os
import numpy as np
import pandas as pd
#数据的读取
# 定义一个读取文件的函数
def load(file_path):
    read_file = open (file_path,'r', encoding = 'UTF-8', errors = 'ignore')   # 打开文件，读取后重新编码
    data = []
    for line in read_file.readlines():  #将文件逐行读入
        row = []   #记录每一行
        lines = line.strip().split("\t")  #strip 去掉每行头尾的空白，split为选择分隔符
        for x in lines:    #将每一行中的元素依次读入对应的list中
            row.append(x)  #每个读取的元素依次加入行中
        data.append(row) #每一行加入到data中
    read_file.close() #读完后，关闭文件夹
    return data
# 数据的查找 （判断是什么数据并做出初步的筛分）
def clean(data):
    if data[2][2] == "Cyclic Voltammetry":
        first_name = [[row[i] for row in data] for i in [0]][0] # 筛选出每个list的第一个字母,并将第一个字母提出来
        data = data[first_name.index("CURVE2") + 3:first_name.index("CURVE3")] # 确定第几圈
        # 选择合适的数据作图
        data_x = [[row[i] for row in data] for i in [2]]
        data_y = [[row[i] for row in data] for i in [3]]
        # 将列表中的列表提取出来并转化为浮点型，每组曲线画两次，保证曲线闭合
        data_x = list(map(float, data_x[0])) * 2
        data_y = list(map(float, data_y[0])) * 2
        # 做出等效的放大，缩小要记得改名字
        data_x = [x * 1000 for x in data_x]  # 横坐标放大1000倍，单位为毫伏
        data_y = [y * 1000 for y in data_y]  # 纵坐标放大1000倍，单位为毫安
        name = ["Cyclic Voltammetry"]
        data = [data_x, data_y] + name
        return data
    elif data[2][2] == "Potentiostatic EIS":
        name = ['Potentiostatic EIS']
        data = data[70:]
        data_x = [[row[i] for row in data] for i in [2]]
        data_y = [[row[i] for row in data] for i in [6]]
        data_x = list(map(float, data_x[0]))
        data_y = list(map(float, data_y[0]))
        name = ["Potentiostatic EIS"]
        data = [data_x, data_y] + name
        return data
    else:
        pass

#将上述“读取，清洗” - 2种过程进行封装，即可定义出处理程序：process
def process(file):
    load_file = load(file)
    clean_file = clean(load_file)
    file = clean_file
    return file

import os
#打开文档选择文件夹
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
Floderpath = filedialog.askdirectory()

#读取文件夹下所有文件，并到处绝对路径至pathnames
path = os.path.join(Floderpath)
filenames = os.listdir(path)
pathnames = [os.path.join(path, filename) for filename in filenames]
#保存图片名字为所读文件夹名字
image_name = path.split('\\')

#创建空的嵌套列表并，并对上述读取的列表进行读取操作，保存在嵌套列表中
data = [[]] * len(pathnames)
for i in range(len(pathnames)):
    data[i] = process(pathnames[i])

#画图
import matplotlib as mlt
import matplotlib.pyplot as plt #导入
from pylab import * #导入所有库
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 默认的像素：[6.0,4.0]，分辨率为100，图片尺寸为 600&400
# 指定dpi=200，图片尺寸为 1200*800
# 指定dpi=300，图片尺寸为 1800*1200
fig = figure(figsize=(8,6), dpi=600)
fig.patch.set_facecolor('white')  #坐标轴背景
plt.grid(linestyle="dotted")  # supported values are '-', '--', '-.', ':', 'None', ' ', '', 'solid', 'dashed', 'dashdot', 'dotted'
ax = plt.gca()
ax.spines['top'].set_visible(False)  # 去掉上边框
ax.spines['right'].set_visible(False)  # 去掉右边框
cmap = plt.cm.get_cmap('Greys')   #获取cmap对象

#判断属于阻抗还是cv，设置合适的坐标轴。
if data[0][2] =="Cyclic Voltammetry":
    plt.xlabel('Vf(mV vs. Ref.)')
    plt.ylabel('Im (mA)')
    plt.title('Cyclic Voltammetry')
elif data[0][2] =="Potentiostatic EIS":
    #阻抗特参
    #设置x轴为log坐标
    plt.xscale("symlog")
    #设置x,y轴标签,及标题
    plt.xlabel('Freq(Hz)')
    plt.ylabel('Zmod(ohm)')
    plt.title('Potentiostatic EIS')
else:
    pass
#导入数据
for i in range(len(pathnames)):
    plt.plot(data[i][0],data[i][1], label = "%s"%filenames[i],linewidth=1.2, linestyle="-")
#生成图例

plt.savefig('%s'%image_name[-1] + '.png', format='png')  #保存为特定类型的图： eps, jpeg, jpg, pdf, pgf, png, ps, raw, rgba, svg, svgz, tif, tiff
plt.show()#展示图片
