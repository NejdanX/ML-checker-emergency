# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'message_read_form.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_read_message_form(object):
    def setupUi(self, read_message_form):
        read_message_form.setObjectName("read_message_form")
        read_message_form.resize(869, 471)
        self.gridLayout = QtWidgets.QGridLayout(read_message_form)
        self.gridLayout.setContentsMargins(0, 3, 0, 3)
        self.gridLayout.setObjectName("gridLayout")
        self.message_text = QtWidgets.QTextBrowser(read_message_form)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.message_text.setFont(font)
        self.message_text.setObjectName("message_text")
        self.gridLayout.addWidget(self.message_text, 1, 0, 1, 2)
        self.btn_agree = QtWidgets.QPushButton(read_message_form)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.btn_agree.setFont(font)
        self.btn_agree.setObjectName("btn_agree")
        self.gridLayout.addWidget(self.btn_agree, 2, 1, 1, 1)
        self.btn_disagree = QtWidgets.QPushButton(read_message_form)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.btn_disagree.setFont(font)
        self.btn_disagree.setObjectName("btn_disagree")
        self.gridLayout.addWidget(self.btn_disagree, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(read_message_form)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.retranslateUi(read_message_form)
        QtCore.QMetaObject.connectSlotsByName(read_message_form)

    def retranslateUi(self, read_message_form):
        _translate = QtCore.QCoreApplication.translate
        read_message_form.setWindowTitle(_translate("read_message_form", "Сообщение"))
        self.btn_agree.setText(_translate("read_message_form", "Подтвердить"))
        self.btn_disagree.setText(_translate("read_message_form", "Отклонить"))
        self.label.setText(_translate("read_message_form", "На основании приведенных ниже данных, подтвердите или отклоните факт ЧС"))