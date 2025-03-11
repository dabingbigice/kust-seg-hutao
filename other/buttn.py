import typing

from PyQt5 import QtCore
from PyQt5.Qt import *


class StartButtn(QWidget):

    def __init__(self, frame, capWindow):
        super().__init__(frame)
        desktop = QDesktopWidget().availableGeometry()
        self.capWindow = capWindow
        self.buttn = QPushButton(frame)
        self.buttn.setText("暂停")
        self.buttn.resize(100, 50)
        self.buttn.move(desktop.width() - desktop.width() // 3, 0)
        self.buttn.clicked.connect(self.clickEvent)

    def clickEvent(self):
        if self.buttn.text() == "暂停":
            print("stop")
            # todo 串口消息
            print("发送串口停止消息")
            self.buttn.setText("开始")
            self.capWindow.stop()
            return
        if self.buttn.text() == "开始":
            print("start")
            # todo 串口消息
            print("发送串口开始消息")
            self.capWindow.start()
            self.buttn.setText("暂停")
