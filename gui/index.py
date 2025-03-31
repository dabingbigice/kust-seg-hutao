import sys
import threading
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
port = 'COM7'
deeplab = DeeplabV3()
my_class = ["background", "hutao_all", "walnut_half"]
import queue

# 创建一个无界队列（默认最大容量为无限大）
shared_photo_frame_0 = queue.Queue(maxsize=1)
shared_photo_ret_0 = queue.Queue(maxsize=1)
shared_photo_frame_1 = queue.Queue(maxsize=1)
shared_photo_ret_1 = queue.Queue(maxsize=1)
cap0 = cv2.VideoCapture(0)
cap1 = cv2.VideoCapture(1)
th_flag = True


# 定义线程要执行的函数
def add_data(shared_list_frame, shared_list_ret,value, cap):
    print('开启多线程成功！！！！')
    while th_flag:
        start1 = time.time()
        # time.sleep(0.015)
        ret, frame = cap.read()
        start2 = time.time()
        shared_list_frame.put(frame, block=True)
        shared_list_ret.put(ret, block=True)
        print(f'{cap}:摄像头读取照片时间{(start2 - start1) * 1000}ms')
        print(f"Photo Added  by {threading.current_thread().name} to{cap}")


class FixedCameraAppChild(QWidget):
    '''
    x,y代表窗口位置
    stm32Serial=串口对象
    cap_port=摄像头编号
    msgLabel=输出标签
    '''

    def __init__(self, parent, msgLabel, x=0, y=0):
        super().__init__(parent)
        # 初始化窗口和摄像头
        self.initUI(x, y)
        self.msgLabel = msgLabel  # 输出消息
        self.msgLabel.adjustSize()  # 输出消息自适应大小

    def initUI(self, x, y):
        # 窗口设置
        self.setWindowTitle("固定尺寸摄像头")
        # 计算屏幕中心坐标
        desktop = QDesktopWidget().availableGeometry()
        # x = (desktop.width() - 512) // 2
        # y = (desktop.height() - 512) // 2
        self.setGeometry(x, y, videoWidth, videoHeight)  # 左上角坐标(0,0)，尺寸512x512
        self.setFixedSize(videoWidth, videoHeight)  # 禁止调整窗口大小
        # 视频显示区域
        self.labelchild = QLabel(self)
        self.labelchild.setFixedSize(videoWidth, videoHeight)  # 固定标签尺寸
        self.labelchild.setAlignment(Qt.AlignCenter)  # 内容居中
        self.labelchild.setStyleSheet("background-color: black;")


class FixedCameraApp(QWidget):
    '''
    x,y代表窗口位置
    stm32Serial=串口对象
    cap_port=摄像头编号
    msgLabel=输出标签
    '''

    def __init__(self, parent, msgLabel, stm32Serial, child_winodw, id, x=0, y=0, time=10):
        super().__init__(parent)
        # 初始化窗口和摄像头
        self.initUI(x, y)
        self.timer = QTimer()  # 定时器
        self.timer.timeout.connect(self.update_frame)  # 插槽
        self.timer_id = self.timer.timerId()
        self.timer.start(time)  # 自动启动刷新
        self.deeplab = deeplab  # 初始化模型
        self.msgLabel = msgLabel  # 输出消息
        self.msgLabel.adjustSize()  # 输出消息自适应大小
        self.flag = 0
        # self.stm32Serial = stm32Serial(port=port, baudrate=9600)  # 发送消息
        self.stm32Serial = stm32Serial  # 发送消息
        self.id = id  # 摄像头编号
        self.time = time
        self.child_winodw = child_winodw
        self.start_th = True

    def stop(self):
        if self.timer.isActive():
            self.timer.stop()

            # 释放摄像头资源（但保持摄像头对象存在以便重启）
        if self.capture0.isOpened():
            self.capture0.release()

    def start(self):
        """重启摄像头输出的核心逻辑"""
        # 检测摄像头状态
        if not self.capture0.isOpened():
            try:
                # 尝试重新打开摄像头（兼容多平台）
                success = self.capture0.open(0)
                if not success:
                    print("摄像头启动失败：设备可能被占用或不存在")
                    return False
            except Exception as e:
                print(f"摄像头初始化异常：{str(e)}")
                return False

        # 启动定时器（如果未运行）
        if not self.timer.isActive():
            self.timer.start()  # 30ms间隔（约33帧/秒）

        # 恢复显示区域（可选）
        self.label.setStyleSheet("background-color: none;")

    def window_detect(self, ret, frame, th, label):
        print(f"正在检测~")
        # todo frame丢进模型里，然后在界面显示融合后的图片
        fps = 0.0
        start1 = time.time()
        if ret:
            frame = cv2.resize(frame, (videoWidth, videoHeight))
            # 格式转变，BGRtoRGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 转变成Image
            frame = Image.fromarray(np.uint8(frame))
            t1 = time.time()
            # 进行检测
            img, text, ratio = self.deeplab.detect_image(frame, count=True, name_classes=my_class)
            t2 = time.time()
            # TODO 检测完成之后开启另外一个线程去显示画面。
            delta_ms = (t2 - t1) * 1000
            print(f"deeplab.detect_image检测速度: {delta_ms:.3f} 毫秒")
            t3 = time.time()
            # 偶数打开控制
            # 0号摄像头处理逻辑

            if ratio > th:
                self.flag = 2
            else:
                self.flag = 3

            # 发送指令
            self.stm32Serial.send_to_stm32(message=str(self.flag))

            # 计算延迟

            #
            # if self.flag == 0:
            #     self.flag = 1
            # else:
            #     self.flag = 0
            frame = np.array(img)

            # RGBtoBGR满足opencv显示格式
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            # print(text)
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
            label.setPixmap(QPixmap.fromImage(q_img))
            self.msgLabel.setText(text)
            self.msgLabel.adjustSize()
            t4 = time.time()
            print(f'模型后处理消耗时间:{(t4 - t3) * 1000}ms')

    def initUI(self, x, y):
        # 窗口设置
        self.setWindowTitle("固定尺寸摄像头")
        # 计算屏幕中心坐标
        desktop = QDesktopWidget().availableGeometry()
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
        if self.start_th:
            self.start_th = False
            thread0 = threading.Thread(target=add_data,
                                       args=(
                                           shared_photo_frame_0, shared_photo_ret_0, "cap0_take_photo!", cap0),
                                       name="photo-th_0")
            thread0.start()
            thread1 = threading.Thread(target=add_data,
                                       args=(
                                           shared_photo_frame_1, shared_photo_ret_1, "cap1_take_photo!", cap1),
                                       name="photo-th_1")
            thread1.start()
            # shared_photo_frame_0[:] = [shared_photo_frame_0[-2:]]
            # shared_photo_frame_1[:] = [shared_photo_frame_1[-2:]]
            # shared_photo_ret_0[:] = [shared_photo_ret_0[-2:]]
            # shared_photo_ret_1[:] = [shared_photo_ret_1[-2:]]

        # while shared_photo_frame_0.qsize() < 1 and shared_photo_frame_1.qsize() < 1:
        #     print('等待摄像头开启')
        frame0 = shared_photo_frame_0.get(timeout=3)
        ret0 = shared_photo_ret_0.get(timeout=3)

        frame1 = shared_photo_frame_1.get(timeout=3)
        ret1 = shared_photo_ret_1.get(timeout=3)

        # todo frame丢进模型里，然后在界面显示融合后的图片
        # fps = 0.0
        # start1 = time.time()
        t1 = time.time()
        self.window_detect(ret0, frame0, 7, self.label)
        t2 = time.time()
        print(f'cap0摄像头处理图片时间:{(t2 - t1) * 1000}ms')
        print(f'-------------------------------------------------------------------------------')

        t3 = time.time()
        self.window_detect(ret1, frame1, 3, self.child_winodw.labelchild)
        t4 = time.time()
        print(f'cap1摄像头处理图片时间:{(t4 - t3) * 1000}ms')
        print(f'-------------------------------------------------------------------------------')

        # if ret1:
        #     frame = cv2.resize(frame1, (videoWidth, videoHeight))
        #     # 格式转变，BGRtoRGB
        #     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #     # 转变成Image
        #     frame = Image.fromarray(np.uint8(frame))
        #     t1 = time.time()
        #     # 进行检测
        #     img, text, ratio = self.deeplab.detect_image(frame, count=True, name_classes=my_class)
        #     t2 = time.time()
        #     # TODO 检测完成之后开启另外一个线程去显示画面。
        #     delta_ms = (t2 - t1) * 1000
        #     print(f"deeplab.detect_image检测速度: {delta_ms:.3f} 毫秒")
        #     t3 = time.time()
        #     # 偶数打开控制
        #     # 0号摄像头处理逻辑
        #     if ratio > 3:
        #         self.flag = 0
        #     else:
        #         self.flag = 1
        #
        #     t3 = time.time()
        #     # 发送指令
        #     self.stm32Serial.send_to_stm32(message=str(self.flag))
        #
        #     # 计算延迟
        #     t4 = time.time()
        #     print(f"串口发送延迟: {t4 - t3:.6f} 毫秒")
        #
        #     #
        #     # if self.flag == 0:
        #     #     self.flag = 1
        #     # else:
        #     #     self.flag = 0
        #     frame = np.array(img)
        #
        #     # RGBtoBGR满足opencv显示格式
        #     frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        #     # print(text)
        #     label_msg = text
        #     fps = (fps + (1. / (t2 - t1))) / 2
        #     fps = (fps + (1. / (time.time() - t1))) / 2
        #     print("fps= %.2f" % (fps))
        #     frame = cv2.putText(frame, "fps= %.2f" % (fps), (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        #
        #     # cv2.imshow("video", frame)
        #     # # 强制缩放到512x512（可能变形）
        #     # frame = cv2.resize(frame, (videoWidth, videoHeight))
        #     # # 颜色空间转换
        #     # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #     # 转换为Qt图像
        #     q_img = QImage(
        #         frame.data,
        #         videoWidth, videoHeight,  # 固定尺寸
        #         frame.strides[0],
        #         QImage.Format_RGB888
        #     )
        #     self.child_winodw.labelchild.setPixmap(QPixmap.fromImage(q_img))
        #     self.msgLabel.setText(text)
        #     self.msgLabel.adjustSize()
        #     t4 = time.time()
        #     print(f'模型1后处理消耗时间:{(t4 - t3) * 1000}ms')
        #     print(f'-------------------------------------------------------------------------------')
        # end2 = time.time()
        # print(f'2号摄像头检测的时间:{(end2 - start2) * 1000}ms')

    def closeEvent(self, event):
        """关闭时释放资源"""
        if self.capture0.isOpened():
            self.capture0.release()
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
    child_window = FixedCameraAppChild(frame, label, x=(desktop.width() - 512) // 2, y=(desktop.height() - 525))

    # 0号摄像头
    capWindow_0 = FixedCameraApp(frame, label, ser_common, child_window, id=0,
                                 x=(desktop.width() - 512) // 2
                                 )
    # capWindow_1 = FixedCameraApp(frame, label, ser_common, id=1, cap_port=video_port + 1,
    #                              x=(desktop.width() - 512) // 2,
    #                              y=(desktop.height() - 512) // 2)
    desktop = QDesktopWidget().availableGeometry()
    # 开启多线程读取数据

    buttn.StartButtn(frame, capWindow_0, x=desktop.width() - desktop.width() // 3, y=0)

    # buttn.StartButtn(frame, capWindow_1, x=desktop.width() - desktop.width() // 3, y=200)
    frame.resize(desktop.width(), desktop.height())
    frame.move(0, 0)
    frame.show()

    sys.exit(app.exec_())
