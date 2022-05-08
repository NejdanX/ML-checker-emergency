from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5 import QtGui, QtCore
from static.forms.message_read_form import Ui_read_message_form
from GUI.Constants import *
from datetime import datetime
import sys


class MessageRead(QWidget, Ui_read_message_form):
    def __init__(self, main_window, data, previous_messages, socket):
        super(MessageRead, self).__init__()
        self.setupUi(self)
        self.data = data
        self.client_socket = socket
        self.previous_messages = previous_messages
        self.main_window = main_window
        self.load_UI()

    def load_UI(self):
        self.setWindowIcon(QtGui.QIcon("../static/image/programming.png"))
        if self.main_window.choice_theme.currentIndex() == 0:
            sheet = 'a:link {color: rgb(77, 231, 231);}'
            self.message_text.document().setDefaultStyleSheet(sheet)
        self.message_text.setAlignment(QtCore.Qt.AlignJustify)
        self.disaster = 'Данное сообщение помечено как ЧС'
        self.non_disaster = 'Данное сообщение не является ЧС'
        self.is_get_context = False
        if self.data['actual_value']:
            self.label.setText(self.disaster)
            self.label.setStyleSheet('color: red')
        elif self.data['actual_value'] is not None:
            self.label.setText(self.non_disaster)
            self.label.setStyleSheet('color: green')
        self.btn_agree.clicked.connect(self.choice)
        self.btn_disagree.clicked.connect(self.choice)
        self.message_text.setOpenLinks(False)
        self.message_text.setOpenExternalLinks(False)
        self.message_text.anchorClicked.connect(self.get_context)
        self.print_info()

    def choice(self):
        if self.sender().text() == 'Подтвердить':
            if self.data['predicted_value']:
                self.label.setText(self.disaster)
                self.label.setStyleSheet('color: red')
            else:
                self.label.setText(self.non_disaster)
                self.label.setStyleSheet('color: green')
        else:
            if not self.data['predicted_value']:
                self.label.setText(self.disaster)
                self.label.setStyleSheet('color: red')
            else:
                self.label.setText(self.non_disaster)
                self.label.setStyleSheet('color: green')

    def print_info(self):
        self.message_text.append(f'<span>ID сообщения: {self.data["ID_message"]}</span>')
        status = "Открыт" if self.data["actual_value"] is None else "Закрыт"
        closing_date = self.data["closing_date"].replace('T', ' ') if self.data["closing_date"] else 'Не определена'
        if self.data['predicted_value'] == 1:
            self.message_text.append(f'<span>Обнаружена ЧС с вероятностью {self.data["probability"]}</span>')
        else:
            self.message_text.append(f'<span>Данное сообщение не относится к ЧС с вероятностью {self.data["probability"]}</span>')
        self.message_text.append(f'<span>Дата: {self.data["sending_date"].replace("T", " ")}</span>')
        self.message_text.append(f'<span>Источник: {self.data["chat_name"]}</span>')
        self.message_text.append(f'<span>Тип источника: {self.data["chat_type"]}</span>')
        self.message_text.append(f'<span>Отправитель: {self.data["sender"]}</span>')
        self.message_text.append(f'<span>Статус: {status}</span>')
        if status == "Открыт":
            self.message_text.append(f'<span>Дата закрытия: {closing_date}</span>')
        self.message_text.append(f'<span><br><br>{self.data["message_text"]}<br></span>')
        self.message_text.append('<a href="https://google.com">Контекст</a><br>')

    def get_context(self):
        if not self.previous_messages and not self.is_get_context:
            self.message_text.append('<br><span>Контекст отсутствует</span>')
            self.is_get_context = True
        elif self.previous_messages and not self.is_get_context:
            self.is_get_context = True
            self.message_text.append('<br><br>'.join([f'<span>От {item["sender"]} {item["sending_date"].replace("T", " ")}'
                                                      f'<br>{item["message_text"]}</span>'
                                                      for item in self.previous_messages]))
        elif self.is_get_context:
            self.is_get_context = False
            self.message_text.clear()
            self.print_info()
        else:
            return 'Нет контекста'

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.disaster == self.label.text():
            value = 1
        elif self.non_disaster == self.label.text():
            value = 0
        else:
            value = None
        close_date = datetime.now().strftime(DATE_FORMAT)
        if value is not None:
            query = f'''UPDATE PredictedMessage
                            SET actual_value = ?, closing_date = ?
                            WHERE ID_message = ?'''
            args = [value, close_date, self.data['ID_message']]
            answer = self.main_window.answer_from_server(EXECUTE_QUERY, query=query,
                                                         args=args)
            if answer[STATUS] == "False":
                message = 'Произошла ошибка записи на сервере. Попробуйте повторить операцию позднее.'
                QMessageBox.warning(self, 'Ошибка записи', message, QMessageBox.Ok)
            for i in range(len(self.main_window.data_about_messages)):
                if self.main_window.data_about_messages[i]['ID_message'] == self.data['ID_message']:
                    self.main_window.data_about_messages[i]['actual_value'] = value
                    self.main_window.data_about_messages[i]['closing_date'] = close_date
        self.main_window.print_table(self.main_window.current_emergency_table, self.main_window.data_about_messages)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MessageRead('', 'Hellooooo', 'Hellooooo', '')
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
