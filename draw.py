import os
import numpy as np
def process(filename):
    '读取文件，并且输出数据位置，与处理好的横纵坐标数据'
    data = []
    with open (filename,encoding = 'UTF-8', errors = 'ignore') as lines:
        for line in lines:
            line = line.split()#按制位符将数据分割
            data.append(line)#读取的文件付给data
    data.remove([])#移掉空集
    #确定采集数据开始位置
    serial_number = []
    for i in range(len(data)):
        if data[i][0] == "#":
            serial_number.append(i+1)
    #确定数据标签
    lable = data[2][2]
    if lable == 'Potentiostatic':
        curve = data[serial_number[1]:]
        x = []
        y = []
        for i in range(len(curve)):
            curve[i].pop #去掉最后的省略号
            x.append(curve[i][2])
            y.append(curve[i][6])
        data_x = list(map(float, x)) #转换成浮点型
        data_y = list(map(float,y))
    elif lable == 'Cyclic':
        number = int(input("你想测的第几圈的cv？"))
        curve = data[serial_number[number - 1]:serial_number[number]-3]
    #提取出原始数据x,y，并且转化类型
        x = []
        y = []
        for i in range(len(curve)):
            curve[i].pop #去掉最后的省略号
            x.append(curve[i][2])
            y.append(curve[i][3])
        data_x = list(map(float, x)) #转换成浮点型
        data_y = list(map(float,y))
    #对cv进行封闭和纵坐标的处理
       # data_x = list(map(float, x))*2
       # data_y = list(map(float,y))*2
        data_x = [x*1000 for x in data_x] #横坐标放大1000倍，单位为毫伏
        data_y = [y*1000*1282.05 for y in data_y] #所×数值为单位面积下的安数值
    return data_x,data_y,lable
#读取文件夹下所有文件，并导出绝对路径至pathnames
Floderpath = r"location"
path = os.path.join(Floderpath)
filenames = os.listdir(path)
flod = []
for i in filenames:
    if os.path.splitext(i)[1] == ".DTA":   # 筛选DTA文件，跳过其他文件
        flod.append(i)
pathnames = [os.path.join(path, filename) for filename in flod]
#保存图片名字为所读文件夹名字
image_name = path.split('\\')
for i in range(len(flod)): #去除后缀.dta,作为图例
    flod[i] = flod[i].strip(".DTA")
### 数据的提取与名字的整合
data = [] * len(pathnames)
for i in range(len(pathnames)):
    data.append(process(pathnames[i]))

import datetime
import matplotlib as mlt
import matplotlib.pyplot as plt #导入
from pylab import *
from scipy.interpolate import make_interp_spline
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

import pandas as pd
import scipy.stats as st
import seaborn as sns
# 默认的像素：[6.0,4.0]，分辨率为100，图片尺寸为 600&400
# 指定dpi=200，图片尺寸为 1200*800
# 指定dpi=300，图片尺寸为 1800*1200
fig = figure(figsize=(8,6), dpi=600)  #设置图片大小和像素
fig.patch.set_facecolor('white')  #坐标轴背景
plt.grid(linestyle="dotted")  # supported values are '-', '--', '-.', ':', 'None', ' ', '', 'solid', 'dashed', 'dashdot', 'dotted'
cmap = plt.cm.get_cmap('hsv')   #获取cmap对象，颜色地图

# 设置横轴的上下限
#xlim(-500,400)
# 设置纵轴的上下限
#ylim(300,2500)

#cv和阻抗 坐标轴名字设置：
if data[0][-1] == "Cyclic":
    plt.xlabel('Vf(mV vs. Ref.)',fontsize = 18)
    plt.ylabel('Im (A/cm${^2}$)',fontsize = 18)
    plt.title('''Comparison of Cyclic Voltammetry ''', fontsize = 20)
    ylim(-400,500) #设置纵坐标
    for i in range(len(pathnames)):
        ci = 0.95 * np.std(data[i][1])/np.mean(data[i][1]) #设定置信区间的范围
        plt.plot(data[i][0],data[i][1], label = "%s"%flod[i],linewidth=1.2, linestyle="-")#画图
        y_min = min(data[i][1])#找到y的最小值
        x_ecoh = data[i][0][data[i][1].index(y_min)] # y相对应x坐标
        plt.annotate(text = int(y_min), 
                 xy=(x_ecoh,y_min))#标记特殊的值
        plt.plot([x_ecoh,x_ecoh],[y_min,-500],color = 'g',lw=0.5)#标记线
        plt.scatter(x_ecoh,y_min, color='w', marker='o', edgecolors='g', s=10) # 把 corlor 设置为空，通过edgecolors来控制颜
       # plt.fill_between(data[i][0], (data[i][1]-ci), (data[i][1]+ci), color='b', alpha=.1)#画出置信区间
elif data[0][-1] == 'Potentiostatic':
    #设置纵轴的上下限
    xlim(10,10000)
    ylim(300,2500)
    plt.xscale("symlog")
    plt.xlabel('Freq(Hz)',fontsize = 18)
    plt.ylabel('Zmod(ohm)', fontsize = 18)
    plt.title('Contrast of Potentiostatic EIS', fontsize = 20)#Contrast of Potentiostatic EIS
    #画出特定属于阻抗的图
    for i in range(len(pathnames)):
        plt.plot(data[i][0],data[i][1], label = "%s"%flod[i],linewidth=1.2, linestyle="-")#导入想要的数据
        #确定1khz位置
        x_1,x_2 =[],[]
        for x in data[i][0]:
            if x >900 :
                x_1.append(x)
            if x <1100:
                x_2.append(x)
        tmp = [val for val in x_1 if val in x_2]#找到x_1与x_2的交集
        lab = data[i][0].index(tmp[0])
        plt.annotate(text = int(data[i][1][lab]), 
                 xy=(data[i][0][lab],data[i][1][lab]))#标记特殊的值
        plt.scatter(data[i][0][lab],data[i][1][lab], color='w', marker='o', edgecolors='g', s=10) # 把 corlor 设置为空，通过edgecolors来控制颜色
    
plt.legend()
plt.savefig(os.path.join(os.path.abspath(path), format('%s')%image_name[-1]+'.svg'))  #以绝对路径保存图片，矢量图格式
plt.show()#展示图片
