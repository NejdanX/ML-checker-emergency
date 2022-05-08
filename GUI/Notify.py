from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication, QDesktopWidget
from PyQt5.QtWidgets import QGridLayout, QMainWindow
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
import sys
import datetime


class Message(QWidget):
    def __init__(self, title, message, parent=None):
        QWidget.__init__(self, parent)
        self.setLayout(QGridLayout())
        self.titleLabel = QLabel(title, self)
        self.titleLabel.setStyleSheet(
            "font-family: 'Roboto', sans-serif; font-size: 14px; font-weight: bold; padding: 0;")
        self.messageLabel = QLabel(message, self)
        self.messageLabel.setStyleSheet(
            "font-family: 'Roboto', sans-serif; font-size: 12px; font-weight: normal; padding: 0;")
        self.buttonClose = QPushButton(self)
        self.buttonClose.setFixedSize(14, 14)
        self.buttonClose.clicked.connect(lambda: self.close)
        self.layout().addWidget(self.titleLabel, 0, 0)
        self.layout().addWidget(self.messageLabel, 1, 0)
        self.layout().addWidget(self.buttonClose, 0, 1, 2, 1)


class Notification(QWidget):
    signNotifyClose = pyqtSignal(str)
    def __init__(self, main, parent = None):
        time = datetime.datetime.now()
        currentTime = str(time.hour) + ":" + str(time.minute) + "_"
        self.LOG_TAG = currentTime + self.__class__.__name__ + ": "
        super(QWidget, self).__init__(parent)
        self.setGeometry(500, 500, 123, 67)
        self.x, self.y = 1000, 1000
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.nMessages = 0
        self.mainLayout = QVBoxLayout(self)
        self.move(QPoint(main.x() + main.width() - self.width(),
                         main.y() + main.height() + 26 - self.height()))

    def move(self, a0: QPoint) -> None:
        super(Notification, self).move(a0)
        self.x = a0.x()
        self.y = a0.y()

    def setNotify(self, title, message):
        self.y -= 67
        self.move(QPoint(self.x, self.y))
        m = Message(title, message, self)
        self.mainLayout.insertWidget(0, m)
        m.buttonClose.clicked.connect(self.onClicked)
        self.nMessages += 1
        self.show()

    def onClicked(self):
        self.mainLayout.removeWidget(self.sender().parent())
        self.sender().parent().deleteLater()
        self.nMessages -= 1
        self.adjustSize()
        self.y += 67
        self.move(QPoint(self.x, self.y))
        if self.nMessages == 0:
            self.close()

    def close_all(self):
        for i in range(self.mainLayout.count()):
            item = self.mainLayout.itemAt(0).widget()
            self.mainLayout.removeWidget(item)
            item.deleteLater()
            self.nMessages -= 1
            self.adjustSize()
            if self.nMessages == 0:
                self.close()


class Example(QWidget):
    counter = 0

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setLayout(QVBoxLayout())
        btn = QPushButton("Send Notify", self)
        self.layout().addWidget(btn)
        self.counter = 0
        self.notification = Notification()
        btn.clicked.connect(self.notify)

    def notify(self):
        self.counter += 1
        self.notification.setNotify("Title{}".format(self.counter),
                                    "message{}".format(self.counter))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Example()
    w.show()
    sys.exit(app.exec_())