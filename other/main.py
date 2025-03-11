# from PyQt5.QtWidgets import  QLabel,QPushButton

from PyQt5.Qt import *

import sys

app = QApplication(sys.argv)


window = QWidget()
window.setWindowTitle("kust-语义分割-核仁质量分选")
window.resize(1200, 600)
window.move(444, 255)

buttn = QPushButton(window)
buttn.move(300,300)
buttn.setText("buttn")


label = QLabel(window)

label.setText("hello")
label.move(200,200)

window.show()


sys.exit(app.exec_())
