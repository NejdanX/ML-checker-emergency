from PyQt5.QtWidgets import QLabel
from PyQt5.Qt import pyqtSignal
from PyQt5.QtGui import QFont


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent):
        QLabel.__init__(self, parent)
        self.border = True

    def mouseReleaseEvent(self, event):
        super(ClickableLabel, self).mouseReleaseEvent(event)
        self.clicked.emit()

    def enterEvent(self, event):
        self.old_family = self.fontInfo().family()
        self.old_size = self.fontInfo().pointSize()
        font = QFont()
        font.setUnderline(True)
        font.setFamily(self.old_family)
        font.setPointSize(self.old_size)
        self.setFont(font)

    def leaveEvent(self, event):
        font = QFont()
        font.setUnderline(False)
        font.setFamily(self.old_family)
        font.setPointSize(self.old_size)
        self.setFont(font)