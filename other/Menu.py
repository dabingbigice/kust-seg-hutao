
from PyQt5.Qt import *

import sys


class Window(QWidget):
    def __int__(self):
        super().__init__()

    def setInitView(self):
        self.setWindowTitle("kust-语义分割-核仁质量分选")
        self.resize(1200, 600)
        self.move(444, 255)
        buttn = QPushButton(self)
        buttn.move(300, 300)
        buttn.setText("buttn")
        def cao():
            print("dianjiwo")
        buttn.clicked.connect(cao)
        label = QLabel(self)
        label.setText("hello")
        label.move(200, 200)

        label.setProperty("test","test")
        print(label.property("test"))
        label.adjustSize()
        self.show()
        buttn.pressed.connect(cao)