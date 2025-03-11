# from PyQt5.QtWidgets import  QLabel,QPushButton

from PyQt5.Qt import *

import sys

def create(window,num):
    for i in range(num):
        new = QWidget(window)
        new.resize(100,100)
        new.move(200,200)
        new.setStyleSheet("background-color:read;")


app = QApplication(sys.argv)


window = QWidget()
window.setWindowTitle("kust-语义分割-核仁质量分选")
window.resize(500, 500)
window.move(300, 300)
create(window,2)


window.show()


sys.exit(app.exec_())
