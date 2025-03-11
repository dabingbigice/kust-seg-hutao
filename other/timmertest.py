# from PyQt5.QtWidgets import  QLabel,QPushButton

from PyQt5.Qt import *

import sys


class Timer_label(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setText("0")
        self.move(400, 200)

    def timerEvent(self, *args, **kwargs):
        print(self.num)
        self.setText(str(self.num))
        self.num = self.num - 1
        if self.num == 0:
            self.killTimer(self.timmer_id)

    def setNumber(self, num):
        self.num = num;

    def start(self, time):
        self.timmer_id = self.startTimer(time)


app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("kust-语义分割-核仁质量分选")
window.resize(1200, 600)
window.move(444, 255)

label = Timer_label(window)
label.setNumber(100)
# label.start(1000)


def msgChange():
    print(label.text())
    label.setText("test")
    label.adjustSize()

buttn = QPushButton(window)
buttn.setText("按钮")
buttn.clicked.connect(msgChange)

buttn.resize(100, 50)
buttn.move(200, 200)
window.show()

sys.exit(app.exec_())
