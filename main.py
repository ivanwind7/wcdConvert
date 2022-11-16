import func
import cv2 as cv
import matplotlib.pyplot as plt

if __name__ == "__main__":
    wcdPath = './0092_20140213_075526_Yolla.wcd' # 文件路径
    imgList = func.wcdConcert(wcdPath)
    img = (imgList[1])
    fileName = '.\\test.jpg' # 保存路径
    # cv.imencode('.jpg', img)[1].tofile(fileName) # 保存图片
    fig, ax = plt.subplots()
    im = ax.imshow(imgList[1], cmap='gray', interpolation='nearest', vmin=0, vmax=255)
    ax.set_aspect(0.31)
    plt.savefig('origin.png')