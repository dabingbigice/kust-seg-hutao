# from PyQt5.QtWidgets import  QLabel,QPushButton

from PyQt5.Qt import *

import sys
from Menu import Window



app = QApplication(sys.argv)

window = Window()
window.setInitView()

sys.exit(app.exec_())
