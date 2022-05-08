# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'report_form.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_report_form(object):
    def setupUi(self, report_form):
        report_form.setObjectName("report_form")
        report_form.resize(1018, 852)
        report_form.setStyleSheet("font: 10pt \"MS Shell Dlg 2\";")
        self.gridLayout = QtWidgets.QGridLayout(report_form)
        self.gridLayout.setObjectName("gridLayout")
        self.label_8 = QtWidgets.QLabel(report_form)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 3, 2, 1, 1)
        self.label_7 = QtWidgets.QLabel(report_form)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 2, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(report_form)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.predicted = QtWidgets.QLineEdit(report_form)
        self.predicted.setReadOnly(True)
        self.predicted.setObjectName("predicted")
        self.gridLayout.addWidget(self.predicted, 0, 3, 1, 1)
        self.emergency_type = QtWidgets.QComboBox(report_form)
        self.emergency_type.setEditable(True)
        self.emergency_type.setObjectName("emergency_type")
        self.gridLayout.addWidget(self.emergency_type, 3, 3, 1, 1)
        self.label_6 = QtWidgets.QLabel(report_form)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 1, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(report_form)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 2, 1, 1)
        self.emergency_class = QtWidgets.QComboBox(report_form)
        self.emergency_class.setObjectName("emergency_class")
        self.emergency_class.addItem("")
        self.emergency_class.addItem("")
        self.emergency_class.addItem("")
        self.emergency_class.addItem("")
        self.emergency_class.addItem("")
        self.emergency_class.addItem("")
        self.gridLayout.addWidget(self.emergency_class, 2, 3, 1, 1)
        self.source = QtWidgets.QLineEdit(report_form)
        self.source.setReadOnly(True)
        self.source.setObjectName("source")
        self.gridLayout.addWidget(self.source, 3, 1, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(report_form)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.operator_actions = QtWidgets.QTextEdit(self.groupBox_3)
        self.operator_actions.setObjectName("operator_actions")
        self.gridLayout_4.addWidget(self.operator_actions, 0, 0, 1, 1)
        self.btn_create_filled_report = QtWidgets.QPushButton(self.groupBox_3)
        self.btn_create_filled_report.setObjectName("btn_create_filled_report")
        self.gridLayout_4.addWidget(self.btn_create_filled_report, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_3, 8, 0, 1, 4)
        self.label_2 = QtWidgets.QLabel(report_form)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.actual = QtWidgets.QLineEdit(report_form)
        self.actual.setObjectName("actual")
        self.gridLayout.addWidget(self.actual, 1, 3, 1, 1)
        self.just_widget = QtWidgets.QWidget(report_form)
        self.just_widget.setMinimumSize(QtCore.QSize(0, 50))
        self.just_widget.setStyleSheet("QWidget#widget: border: 1px solid black;\n"
"")
        self.just_widget.setObjectName("just_widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.just_widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_12 = QtWidgets.QLabel(self.just_widget)
        self.label_12.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_12.setWordWrap(True)
        self.label_12.setObjectName("label_12")
        self.verticalLayout.addWidget(self.label_12)
        self.gridLayout.addWidget(self.just_widget, 5, 0, 1, 4)
        self.label = QtWidgets.QLabel(report_form)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.sender_message = QtWidgets.QLineEdit(report_form)
        self.sender_message.setReadOnly(True)
        self.sender_message.setObjectName("sender_message")
        self.gridLayout.addWidget(self.sender_message, 2, 1, 1, 1)
        self.id_message = QtWidgets.QLineEdit(report_form)
        self.id_message.setReadOnly(True)
        self.id_message.setObjectName("id_message")
        self.gridLayout.addWidget(self.id_message, 0, 1, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(report_form)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.impact_and_scale = QtWidgets.QTextEdit(self.groupBox_2)
        self.impact_and_scale.setObjectName("impact_and_scale")
        self.gridLayout_3.addWidget(self.impact_and_scale, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_2, 7, 0, 1, 4)
        self.groupBox = QtWidgets.QGroupBox(report_form)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.emergency_description = QtWidgets.QTextEdit(self.groupBox)
        self.emergency_description.setObjectName("emergency_description")
        self.gridLayout_2.addWidget(self.emergency_description, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 6, 0, 1, 4)
        self.label_3 = QtWidgets.QLabel(report_form)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.receive_date = QtWidgets.QLineEdit(report_form)
        self.receive_date.setObjectName("receive_date")
        self.gridLayout.addWidget(self.receive_date, 1, 1, 1, 1)

        self.retranslateUi(report_form)
        QtCore.QMetaObject.connectSlotsByName(report_form)

    def retranslateUi(self, report_form):
        _translate = QtCore.QCoreApplication.translate
        report_form.setWindowTitle(_translate("report_form", "Окно формирования отчёта"))
        self.label_8.setText(_translate("report_form", "Виды ЧС (по классу)"))
        self.label_7.setText(_translate("report_form", "Класс ЧС"))
        self.label_4.setText(_translate("report_form", "Источник"))
        self.label_6.setText(_translate("report_form", "Ответ эксперта"))
        self.label_5.setText(_translate("report_form", "Ответ системы о ЧС"))
        self.emergency_class.setItemText(0, _translate("report_form", "Техногенная"))
        self.emergency_class.setItemText(1, _translate("report_form", "Антропогенная"))
        self.emergency_class.setItemText(2, _translate("report_form", "Природная"))
        self.emergency_class.setItemText(3, _translate("report_form", "Экологическая"))
        self.emergency_class.setItemText(4, _translate("report_form", "Социальная"))
        self.emergency_class.setItemText(5, _translate("report_form", "Смешанная"))
        self.groupBox_3.setTitle(_translate("report_form", "Предпринятые действия для предотвращения последствий ЧС или их минимизации"))
        self.btn_create_filled_report.setText(_translate("report_form", "Создать отчёт"))
        self.label_2.setText(_translate("report_form", "Дата получения"))
        self.label_12.setText(_translate("report_form", "Воспользуйтесь полями ниже, чтобы добавить описание ЧС и ваших действий для её предотвращение. Вы можете сохранить отчёт с незаполненными полями, чтобы заполнить их в вашем текстовом редакторе самостоятельно."))
        self.label.setText(_translate("report_form", "ID сообщения"))
        self.groupBox_2.setTitle(_translate("report_form", "Последствия ЧС и её масштаб"))
        self.groupBox.setTitle(_translate("report_form", "Краткое описание ЧС, причины её возникновения"))
        self.label_3.setText(_translate("report_form", "Отправитель"))
