import sys
import time

import cv2
import numpy as np
import torch
from PIL import Image

from PyQt5.Qt import *

from model.deeplab import DeeplabV3
from other import buttn
from msg_send import stm32Serial

videoWidth = 512
videoHeight = 512
video_port = 0 + cv2.CAP_DSHOW
port = 'COM4'
deeplab = DeeplabV3()


class FixedCameraApp(QWidget):
    '''
    x,y代表窗口位置
    stm32Serial=串口对象
    cap_port=摄像头编号
    msgLabel=输出标签
    '''

    def __init__(self, parent, msgLabel, stm32Serial, id, cap_port=video_port, x=0, y=0):
        super().__init__(parent)
        # 初始化窗口和摄像头
        self.initUI(x, y)
        self.capture = cv2.VideoCapture(cap_port)  # 直接打开摄像头
        self.timer = QTimer()  # 定时器
        self.timer.timeout.connect(self.update_frame)  # 插槽
        self.timer_id = self.timer.timerId()
        self.timer.start(0)  # 自动启动刷新
        self.deeplab = deeplab  # 初始化模型
        self.msgLabel = msgLabel  # 输出消息
        self.msgLabel.adjustSize()  # 输出消息自适应大小
        self.flag = 0
        # self.stm32Serial = stm32Serial(port=port, baudrate=9600)  # 发送消息
        self.stm32Serial = stm32Serial  # 发送消息
        self.id = id  # 摄像头编号

    def stop(self):
        if self.timer.isActive():
            self.timer.stop()

            # 释放摄像头资源（但保持摄像头对象存在以便重启）
        if self.capture.isOpened():
            self.capture.release()

    def start(self):
        """重启摄像头输出的核心逻辑"""
        # 检测摄像头状态
        if not self.capture.isOpened():
            try:
                # 尝试重新打开摄像头（兼容多平台）
                success = self.capture.open(video_port)
                if not success:
                    print("摄像头启动失败：设备可能被占用或不存在")
                    return False
            except Exception as e:
                print(f"摄像头初始化异常：{str(e)}")
                return False

        # 启动定时器（如果未运行）
        if not self.timer.isActive():
            self.timer.start()

        # 恢复显示区域（可选）
        self.label.setStyleSheet("background-color: none;")

    def initUI(self, x, y):
        # 窗口设置
        self.setWindowTitle("固定尺寸摄像头")

        # 计算屏幕中心坐标
        # desktop = QDesktopWidget().availableGeometry()
        # x = (desktop.width() - 512) // 2
        # y = (desktop.height() - 512) // 2


        self.setGeometry(x, y, videoWidth, videoHeight)  # 左上角坐标(0,0)，尺寸512x512
        self.setFixedSize(videoWidth, videoHeight)  # 禁止调整窗口大小
        # 视频显示区域
        self.label = QLabel(self)
        self.label.setFixedSize(videoWidth, videoHeight)  # 固定标签尺寸
        self.label.setAlignment(Qt.AlignCenter)  # 内容居中
        self.label.setStyleSheet("background-color: black;")

    def update_frame(self):
        """强制缩放画面到512x512像素"""
        ret, frame = self.capture.read()
        print(f"正在检测~")
        print(f'--------------------------start-----------------------------------------------------')
        fps = 0.0
        if ret:
            frame = cv2.resize(frame, (videoWidth, videoHeight))
            # 格式转变，BGRtoRGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 转变成Image
            frame = Image.fromarray(np.uint8(frame))
            t1 = time.time()
            # 进行检测
            img, text, hutao_ratio = self.deeplab.detect_image(frame, count=True, name_classes=["background", "hutao"])
            t2 = time.time()
            # TODO 检测完成之后开启另外一个线程去显示画面。
            delta_ms = (t2 - t1) * 1000
            print(f"deeplab.detect_image检测速度: {delta_ms:.3f} 毫秒")

            # 偶数打开控制
            # 0号摄像头处理逻辑
            if self.id == 0:
                if hutao_ratio > 2:
                    self.flag = 0
                else:
                    self.flag = 1

            # 1号摄像头处理逻辑
            if self.id == 1:
                if hutao_ratio > 2:
                    self.flag = 2
                else:
                    self.flag = 3

            t3 = time.time()
            # 发送指令
            self.stm32Serial.send_to_stm32(message=str(self.flag))
            # 计算延迟
            t4 = time.time()
            print(f"串口发送延迟: {t4 - t3:.3f} 毫秒")


            frame = np.array(img)

            # RGBtoBGR满足opencv显示格式
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            fps = (fps + (1. / (t2 - t1))) / 2
            fps = (fps + (1. / (time.time() - t1))) / 2
            print("fps= %.2f" % (fps))
            frame = cv2.putText(frame, "fps= %.2f" % (fps), (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # cv2.imshow("video", frame)
            # # 强制缩放到512x512（可能变形）
            # frame = cv2.resize(frame, (videoWidth, videoHeight))
            # # 颜色空间转换
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 转换为Qt图像
            q_img = QImage(
                frame.data,
                videoWidth, videoHeight,  # 固定尺寸
                frame.strides[0],
                QImage.Format_RGB888
            )
            self.label.setPixmap(QPixmap.fromImage(q_img))
            self.msgLabel.setText(text)
            self.msgLabel.adjustSize()
            t4 = time.time()
            print(f'模型后处理消耗时间:{(t4 - t3) * 1000}ms')
            print(f'--------------------------end-----------------------------------------------------')

    def closeEvent(self, event):
        """关闭时释放资源"""
        if self.capture.isOpened():
            self.capture.release()
        self.timer.stop()
        event.accept()
        self.stm32Serial.close_serial()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 分辨率数值
    desktop = QDesktopWidget().availableGeometry()

    frame = QWidget()
    label = QLabel(frame)
    label.move((desktop.width() - 512) // 2, 512)
    label.setText("test")
    ser_common = stm32Serial(port=port, baudrate=9600)
    # 0号摄像头
    capWindow_0 = FixedCameraApp(frame, label, ser_common, id=0, cap_port=video_port, x=(desktop.width() - 512) // 2)
    capWindow_1 = FixedCameraApp(frame, label, ser_common, id=1, cap_port=video_port + 1,
                                 x=(desktop.width() - 512) // 2,
                                 y=(desktop.height() - 512) // 2)
    desktop = QDesktopWidget().availableGeometry()
    buttn.StartButtn(frame, capWindow_0, x=desktop.width() - desktop.width() // 3, y=0)
    buttn.StartButtn(frame, capWindow_1, x=desktop.width() - desktop.width() // 3, y=200)
    frame.resize(desktop.width(), desktop.height())
    frame.move(0, 0)
    frame.show()

    sys.exit(app.exec_())
