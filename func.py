from pactetclass import waterColumnDatagram
import os
import string
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv

# 将小端16进制byte转换成大端16进制string
def bigSmallEndConvert(data, Size) -> string:
    hexString = data.hex() # 获得数据的16进制字符串
    convertHexString = '' # 创建转换后字符串
    for i in range (Size*2-1, -1, -1): # 从字符串末尾向前循环
        if(i % 2 == 0): # 跳过索引为偶数的循环
            continue
        # 将一组两个的字符添加至转换后字符串
        convertHexString += hexString[i-1] 
        convertHexString += hexString[i]
    return convertHexString

# 获取数据包大小
def getPacketSize(file) -> int:
    packetSize_Small_bytes = file.read(4) # 获取数据包前四字节（即数据包大小）
    packetSize_Big_String = bigSmallEndConvert(packetSize_Small_bytes, 4) # 将数据包大小的16进制小端表示转换成16进制大端字符串
    packetSize = int(packetSize_Big_String, 16) # 16进制字符串转10进制int
    return packetSize

# 获取数据包类型
def getPacketType(file) -> string:
    bf = file.read(2).hex() # 继续获取两字节数据包的16进制字符串
    packetType = bf[2] + bf[3] # 后一字节即为数据包类型
    return packetType

#将灰度数组映射为直方图字典,nums表示灰度的数量级
def arrayToHist(grayArray,nums):
    if(len(grayArray.shape) != 2):
        print("length error")
        return None
    w,h = grayArray.shape
    hist = {}
    for k in range(nums):
        hist[k] = 0
    for i in range(w):
        for j in range(h):
            if(hist.get(grayArray[i][j]) is None):
                hist[grayArray[i][j]] = 0
            hist[grayArray[i][j]] += 1
    #normalize
    n = w*h
    for key in hist.keys():
        hist[key] = float(hist[key])/n
    return hist

#计算累计直方图计算出新的均衡化的图片,nums为灰度数,256
def equalization(grayArray,h_s,nums):
    #计算累计直方图
    tmp = 0.0
    h_acc = h_s.copy()
    for i in range(256):
        tmp += h_s[i]
        h_acc[i] = tmp

    if(len(grayArray.shape) != 2):
        print("length error")
        return None
    w,h = grayArray.shape
    des = np.zeros((w,h),dtype = np.uint8)
    for i in range(w):
        for j in range(h):
            des[i][j] = int((nums - 1)* h_acc[grayArray[i][j] ] +0.5)
    return des

# wcd转图片，filePath图像数组，返回图像数组
def wcdConcert(filePath):

    wcdFileSize = os.path.getsize(filePath) # 文件大小
    wcdFile = open(filePath, 'rb') # 以二进制形式打开文件

    sc = 0 # 计数器
    arrayBoss = [] # 最后的总数组
    ptr = 0 # 文件指针位置
    outerLoopFlag = True
    # 在wcd文件中循环搜索wcd包
    while outerLoopFlag:

        # 如果指针位置超出文件，则退出循环
        if(ptr >= wcdFileSize):
            break

        packetSize = getPacketSize(wcdFile) # 获取数据包大小
        packetType = getPacketType(wcdFile) # 获取数据包类型
        wcdFile.seek(ptr) # 重新定位到开头

        if(packetType != '6b'): #若不是wcd则跳过
            packetStartLocation = wcdFile.tell() + 4 # 数据包起始坐标（不包括数据包大小）
            ptr = packetStartLocation + packetSize # 修改文件指针位置
            wcdFile.seek(ptr) # 定位到数据包末尾
        else: # 若是wcd包则进行读取
            tempArray = [] # 单个数据包采样的临时数组
            interLoopFlag = True

            # 循环解析隶属于一幅图的数据包们
            while interLoopFlag:
                packetSize = getPacketSize(wcdFile) # 获取数据包大小
                packetType = getPacketType(wcdFile) # 获取数据包类型
                wcdFile.seek(ptr) # 重新定位到开头
                if(packetType != '6b'): #若不是wcd则跳过
                    packetStartLocation = wcdFile.tell() + 4 # 数据包起始坐标（不包括数据包大小）
                    ptr = packetStartLocation + packetSize # 修改文件指针位置
                    wcdFile.seek(ptr) # 定位到数据包末尾
                    continue
                packetStartLocationWithSize = wcdFile.tell() # 数据包起始坐标(包括数据包大小)
                packetStartLocation = packetStartLocationWithSize + 4 # 数据包起始坐标(不包括数据包大小)
                wcdObject = waterColumnDatagram()  # 创建一个waterColumnDatagram对象

                # 对数据包的header进行遍历
                for i in range(0, len(wcdObject.header)):
                    itemSize = wcdObject.header[i][1] # 条目大小
                    item = wcdFile.read(itemSize) # 读取条目
                    valueHex = bigSmallEndConvert(item, itemSize) # 条目16进制字符串
                    value = int(valueHex, 16) # 条目10进制表示
                    wcdObject.__setattr__(wcdObject.header[i][0], value) # 将数据写入对象中

                # 如果这是这张图的最后一个数据包，则设置循环条件为False
                if wcdObject.Number_of_datagrams == wcdObject.Datagram_numbers:
                    interLoopFlag = False

                # 跳过Ntx
                wcdFile.seek(wcdFile.tell() + 6 * (wcdObject.Number_of_transmit_sectors))
                
                # 对数据包的Nrx进行遍历
                for i in range(0, wcdObject.Number_of_beams_in_this_daragram):
                    # 对数据包的NrxHeader进行遍历
                    for i in range(0, len(wcdObject.Nrx)):
                        itemSize = wcdObject.Nrx[i][1] # 条目大小
                        item = wcdFile.read(itemSize) # 读取条目
                        valueHex = bigSmallEndConvert(item, itemSize) # 条目16进制字符串
                        value = int(valueHex, 16) # 条目10进制表示
                        wcdObject.__setattr__(wcdObject.Nrx[i][0], value) # 将数据写入对象中         
                
                    oneSampleArray = [] # 单次采样数组
                    # 对每个波束的采样进行遍历并保存
                    for i in range (0, wcdObject.Ntr_Number_of_samples):
                        oneSampleArray.append(int(wcdFile.read(1).hex(), 16))

                    # 将单次采样添加至数据包采样临时数组中
                    tempArray.append(oneSampleArray)
    
                ptr = packetStartLocation + packetSize # 修改文件指针位置
                wcdFile.seek(ptr) # 定位到下一个数据包开头
            
            # 将数据包采样临时数组添加至总数组中
            arrayBoss.append(tempArray)
            # 计数
            sc = sc + 1
            print('已解析', sc, '个图像矩阵')
            
    # 矩阵处理
    print('图像矩阵处理中...')
    for i in range(0, len(arrayBoss)):
        # 找出一幅图的最大采样数
        max = 0
        for j in range(0, len(arrayBoss[i])):
            if len(arrayBoss[i][j]) > max :
                max = len(arrayBoss[i][j])
        # 补255
        for j in range(0, len(arrayBoss[i])):
            if len(arrayBoss[i][j]) < max :
                for k in range(len(arrayBoss[i][j]), max):
                    arrayBoss[i][j].append(255)
        # 矩阵转置
        arrayBoss[i] = np.array(arrayBoss[i]).T

        # 归一化
        # arrayBoss[i] = 255*(temp-np.min(temp))/(np.max(temp)-np.min(temp))

        # 均衡化
        # hist_s = arrayToHist(temp, 256)
        # im_d = equalization(temp, hist_s, 256)
        # arrayBoss[i] = im_d

    print('* * * 图像矩阵解析完成，共计', sc, '幅图像 * * *')

    return arrayBoss


    # 绘制
    while True:
        num = input('请输入要绘制的图像编号(输入q结束)：')
        try:
            if num == 'q':
                break
            else:
                if 1 <= int(num) and int(num) <= sc:
                #     print('图像绘制中...')
                #     fig, ax = plt.subplots()
                #     im = ax.imshow(arrayBoss[int(num) - 1], cmap='gray', interpolation='nearest', vmin=0, vmax=255)
                #     ax.set_aspect(0.31)
                #     plt.savefig('origin.png')
                #     # plt.show()
                #     plt.close()

                #     # 伪彩
                #     img = cv.imread('./origin.png')
                #     im_color = cv.applyColorMap(img, cv.COLORMAP_OCEAN)
                #     cv.imshow('colorImg', im_color)
                #     print('图像绘制完成...')
                #     cv.imwrite('./color.png', im_color)
                # else:
                    continue
        except:
            continue