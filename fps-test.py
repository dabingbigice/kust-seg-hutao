import cv2

from model.deeplab import DeeplabV3

deeplab = DeeplabV3()  # 初始化模型
deeplab.detect_image(cv2.imread('model/img/h1.JPG'),count=False)