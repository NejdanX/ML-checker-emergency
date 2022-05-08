from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QMenu, QAction, QMessageBox, QWidget
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QAbstractItemView
from PyQt5.QtGui import QIcon, QColor, QPainter, QBrush
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5 import QtCore, QtGui
from PyQt5.QtTest import QTest
from math import ceil
from GUI.Report import Report
import json
from GUI.Charts import MplCanvas
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix
from GUI.MessageRead import MessageRead
from GUI.Constants import *
from static.forms.main_window import Ui_MainWindow
import sys
import hashlib
from GUI.Notify import Notification
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import threading
import playsound
print(sys.path)


class SignalNotification(QObject):
    open = pyqtSignal()


class MyPopup(QWidget):
    def __init__(self):
        QWidget.__init__(self)

    def paintEvent(self, e):
        dc = QPainter(self)
        dc.drawLine(0, 0, 100, 100)
        dc.drawLine(100, 0, 0, 100)


class Client(QMainWindow, Ui_MainWindow):
    def __init__(self, app, client_socket, login, jwt_token, id_employee, full_name, default_theme):
        super(Client, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon("../static/image/programming.png"))
        self.client_socket = client_socket
        self.server_available = False
        self.id_employee = id_employee
        self.full_name = full_name
        self.jwt_token = jwt_token
        self.timeout = 10
        self.app = app
        self.login = login
        self.current_emergency_table = self.table_high
        self.data_about_messages = []
        self.default_theme = default_theme
        self.fig = plt.figure(figsize=(5, 4), dpi=100, tight_layout=True)
        self.sc = MplCanvas(self.fig)
        self.notification = Notification(self)
        self.screen = self.app.primaryScreen()
        self.coord_before_hide = self.notification.pos()
        # thread_connection = threading.Thread(target=self.try_connect, daemon=True)
        # thread_connection.start()
        self.notification.setStyleSheet('background: #42484f')
        self.signal_notification = SignalNotification()
        self.signal_notification.open.connect(self.show_notification)
        self.btn_update_table.clicked.connect(lambda: self.print_table(self.current_emergency_table, self.data_about_messages))
        self.initUi()
        self.socket_thread = threading.Thread(target=self.check_new_disaster_message, daemon=True)
        self.socket_thread.start()

    def initUi(self):
        with open('../static/settings/setting.json', 'r', encoding='utf8') as file:
            self.json_data = json.load(file)
        default_date = (2000, 1, 1, 0, 0, 0)
        self.calendarWidget.clicked.connect(lambda: self.dt_begin.setDateTime(QtCore.QDateTime(*default_date)) or
                                                    self.dt_end.setDateTime(QtCore.QDateTime(*default_date)))
        self.load_settings()
        self.get_all_chats()
        self.setWindowTitle('Вы вошли как ' + self.login)
        self.btn_create_doc.clicked.connect(self.create_document)
        self.tabWidget.currentChanged.connect(lambda: self.print_table(self.current_emergency_table,
                                                                         self.data_about_messages)
                                                                         if self.tabWidget.currentIndex() == 0 else None)
        self.check_all_date.setChecked(True)
        self.radio_count_disaster.setChecked(True)
        self.combo_sort.currentIndexChanged.connect(lambda: self.print_table(self.current_emergency_table,
                                                                             self.data_about_messages))
        self.btn_graph.clicked.connect(self.graphic)
        self.btn_clear.clicked.connect(lambda: self.sc.axes.cla() or self.sc.draw() or self.sc.axes.set_aspect('auto'))
        self.print_only_unread.clicked.connect(lambda: self.print_table(self.current_emergency_table,
                                                                        self.data_about_messages))
        self.cancel_sort.clicked.connect(lambda:  self.print_table(self.current_emergency_table,
                                                                   self.data_about_messages))
        self.btn_send.clicked.connect(self.test_check_message)
        self.layout_for_graph.setContentsMargins(0, 0, 0, 0)
        self.toolbar = NavigationToolbar(self.sc, self)
        self.toolbar.setStyleSheet("color: black; background-color: white; font-size: 12px;")
        self.layout_for_graph.addWidget(self.toolbar)
        self.layout_for_graph.addWidget(self.sc)
        self.result_window.setContextMenuPolicy(Qt.CustomContextMenu)
        self.result_window.customContextMenuRequested.connect(self.context)
        self.result_window.setWordWrap(Qt.TextWrapAnywhere)
        self.emergency_management.tabBarClicked.connect(self.get_data)
        self.tables = [self.table_low, self.table_medium, self.table_high]
        self.setting_table()
        self.change_theme(self.choice_theme.currentIndex())
        self.choice_theme.currentIndexChanged.connect(self.change_theme)
        self.get_data(self.emergency_management.currentIndex())

    def test_check_message(self):
        text = self.message_input.toPlainText()
        answer = self.answer_from_server(command='test', message=text)
        if answer[STATUS]:
            self.result_window.addItem(f'{text}\n{answer["answer"]}\n'
                                       f'Вероятность: {round(max(answer["probability"]), 4) * 100}%\n')

    def resizeEvent(self, event):
        self.notification.move(QtCore.QPoint(self.x() + self.width() - self.notification.width(),
                                             self.y() + self.height() + 26 -
                                             self.notification.height()))

    def moveEvent(self, a0):
        self.notification.move(self.notification.pos() + (a0.pos() - a0.oldPos()))

    def hideEvent(self, a0: QtGui.QHideEvent) -> None:
        size = self.screen.availableGeometry()
        print(size)
        self.coord_before_hide = self.notification.pos()
        self.notification.move(QtCore.QPoint(size.width() - self.notification.width(), size.height() - self.notification.height()))

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        self.notification.move(self.coord_before_hide)
        if self.notification.mainLayout.count() > 0:
            self.notification.show()

    def check_new_disaster_message(self):
        threading.Timer(POLLING_RATE, self.check_new_disaster_message).start()
        answer = self.answer_from_server('get_new_disaster_message')
        if answer[STATUS] and answer[QUERY_RESULT]:
            self.signal_notification.open.emit()
            if self.current_emergency_table == self.table_high:
                self.data_about_messages += answer[QUERY_RESULT]
                self.print_table(self.table_high, self.data_about_messages)

    def show_notification(self):
        self.notification.setNotify('Уведомление', 'Новое сообщение с меткой ЧС')

    def popup(self):
        self.w = MyPopup()
        self.w.setGeometry(QtCore.QRect(100, 100, 400, 200))
        self.w.show()

    def get_all_chats(self):
        query = 'SELECT DISTINCT chat_name FROM PredictedMessage'
        data = self.answer_from_server(EXECUTE_QUERY, query=query, args=list())
        self.combo_chats.clear()
        self.combo_chats.addItem('Все')
        self.combo_chats.addItems([item['chat_name'] for item in data[QUERY_RESULT]])

    def answer_from_server(self, command, **kwargs):
        kwargs['command'] = command
        kwargs['jwt_token'] = self.jwt_token
        self.client_socket.sendto(json.dumps(kwargs).encode(), (SERVER_ADDRESS, SERVER_PORT))
        answer = ''
        try:
            info_about_size = self.client_socket.recv(32).decode('utf8')
            print(info_about_size)
            message_length = json.loads(info_about_size)['count_bytes']
        except Exception as e:
            print(e)
            QMessageBox.warning(self, 'Ошибка чтения данных', 'Во время чтения данных от сервера произошла ошибка',
                                QMessageBox.Ok)
            return {STATUS: False, QUERY_RESULT: []}
        message_length = ceil(int(message_length) / 1024)
        for i in range(message_length):
            answer += self.client_socket.recv(1024).decode('utf8')
            if answer.count('{') == answer.count('}'):
                break
        try:
            json_data = json.loads(answer)
            print(json_data)
            return json_data
        except Exception as e:
            print(e)
            return {STATUS: False, QUERY_RESULT: []}

    def change_theme(self, index):
        if index == 0:
            self.current_theme = 'dark'
            with open('../static/css/darkStyle.css') as file:
                self.app.setStyleSheet(file.read())
        else:
            self.current_theme = 'light'
            self.app.setStyleSheet(self.default_theme)

    def load_settings(self):
        self.choice_theme.setCurrentIndex(self.json_data['theme'] == 'white')
        self.print_only_unread.setChecked(self.json_data['hide_read'])
        self.count_context.setValue(self.json_data['count_previous_message'])

    def get_data(self, index):
        if index == 0:
            self.current_emergency_table = self.table_high
            query = '''SELECT * FROM PredictedMessage WHERE predicted_value = 1 AND ID_employee = ?'''
            self.data_about_messages = self.answer_from_server(EXECUTE_QUERY, query=query, parse_date=True,
                                                               args=[self.id_employee])[QUERY_RESULT]
            self.print_table(self.table_high, self.data_about_messages)
        elif index == 1:
            self.current_emergency_table = self.table_medium
            query = '''SELECT * FROM PredictedMessage
                           WHERE probability BETWEEN 0.35 AND 0.5 AND predicted_value = 0 AND ID_employee = ?'''
            self.data_about_messages = self.answer_from_server(EXECUTE_QUERY, query=query, parse_date=True,
                                                               args=[self.id_employee])[QUERY_RESULT]
            self.print_table(self.table_medium, self.data_about_messages)
        else:
            self.current_emergency_table = self.table_low
            query = '''SELECT * FROM PredictedMessage
                           WHERE probability < 0.35 AND ID_employee = ?'''
            self.data_about_messages = self.answer_from_server(EXECUTE_QUERY, query=query, parse_date=True,
                                                               args=[self.id_employee])[QUERY_RESULT]
            self.print_table(self.table_low, self.data_about_messages)

    def print_table(self, table, data):
        table.setRowCount(0)
        data.sort(key=lambda x: x['sending_date'], reverse=True)
        sort_column = SORT_COLUMN[self.combo_sort.currentText()]
        is_reverse = True if sort_column in ['sending_date', 'sender', 'probability'] else False
        data.sort(key=lambda x: x[sort_column], reverse=is_reverse)
        if not self.cancel_sort.isChecked():
            data.sort(key=lambda x: x['actual_value'] is None, reverse=True)
        for i in range(len(data)):
            if self.print_only_unread.isChecked() and data[i]['actual_value'] is not None:
                continue
            table.setRowCount(table.rowCount() + 1)
            for j, key in enumerate(list(data[i].keys())[:3] + list(data[i].keys())[4:-2]):
                value = data[i][key]
                if key == 'predicted_value':
                    value = 'Да' if value else 'Нет'
                if key == 'actual_value':
                    if value is None:
                        value = 'Нет данных'
                    elif value:
                        value = 'Да'
                    else:
                        value = 'Нет'
                if key == 'sending_date':
                    value = data[i][key].replace('T', ' ')
                item = QTableWidgetItem(str(value))
                table.setItem(table.rowCount() - 1, j, item)
            if data[i]['actual_value'] is None:
                if self.current_theme == 'dark':
                    self.color_row(table, table.rowCount() - 1, QColor(224, 225, 227))
                else:
                    self.color_row(table, table.rowCount() - 1, QColor(0, 0, 0))
            else:
                if self.current_theme == 'dark':
                    self.color_row(table, table.rowCount() - 1, QColor(110, 126, 138))
                else:
                    self.color_row(table, table.rowCount() - 1, QColor(128, 128, 128))

    def color_row(self, table, row, color):
        """Красит строку, в зависимости от того, прочитано сообщение или нет"""
        for i in range(table.columnCount()):
            table.item(row, i).setForeground(QBrush(color))

    def setting_table(self):
        header = ['ID', 'Сообщение', 'Источник', 'Дата', 'Отправитель', 'Вероятность', 'ЧС', 'Эксперт']
        for table in self.tables:
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table.setColumnCount(8)
            table.setHorizontalHeaderLabels(header)
            table.resizeColumnsToContents()
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
            table.cellActivated.connect(self.open_message)

    def open_message(self, row, col):
        ID = int(self.sender().item(row, 0).text())
        data = {}
        previous_messages = {}
        for index, item in enumerate(self.data_about_messages[::-1]):
            if item['ID_message'] == ID:
                data = item
                previous_messages = []
                count = 0
                for d in self.data_about_messages:
                    if d['ID_message'] < ID:
                        count += 1
                        previous_messages.append(d)
                        if count >= self.count_context.value():
                            break
                break
        print(data)
        print(previous_messages)
        self.rm = MessageRead(self, data, previous_messages, self.client_socket)
        self.rm.show()

    def context(self, point):
        """Контекстное меню"""
        self.point = point
        # menu = QMenu()
        # if self.chat.itemAt(point):
        #     open_message = QAction('Раскрыть сообщение', menu)
        #     delete_message = QAction('Удалить сообщение', menu)
        #     open_message.triggered.connect(self.open_message)
        #     delete_message.triggered.connect(self.delete_message)
        #     menu.addActions([open_message, delete_message])
        # menu.exec(self.chat.mapToGlobal(point))

    def react(self, json_data):
        prob_disaster = json_data['probability']
        if prob_disaster < 0.35:
            pass
        elif prob_disaster < 0.5:
            self.tabWidget.setCurrentIndex(0)
            self.emergency_management.setCurrentIndex(1)
            playsound.playsound('../static/alert.mp3', True)
        else:
            self.tabWidget.setCurrentIndex(0)
            self.emergency_management.setCurrentIndex(0)
            playsound.playsound('../static/alert.mp3', True)
        self.get_data(self.emergency_management.currentIndex())

    def create_document(self):
        row = self.current_emergency_table.currentRow()
        item = self.current_emergency_table.item(row, 0)
        if item == -1:
            return
        ID = int(self.current_emergency_table.item(row, 0).text())
        data = {}
        for index, item in enumerate(self.data_about_messages[::-1]):
            if item['ID_message'] == ID:
                data = item
        self.report_window = Report(self.full_name, data)
        self.report_window.show()

    def graphic(self):
        QTest.mouseClick(self.btn_clear, Qt.LeftButton)
        chat = self.combo_chats.currentText()
        chat = '%' if chat == 'Все' else chat
        result = {}
        # Матрица ошибок
        if self.radio_pos_neg.isChecked():
            if self.check_all_date.isChecked():
                query = f'''SELECT predicted_value, actual_value FROM PredictedMessage
                                    WHERE actual_value IS NOT NULL AND chat_name LIKE ?'''
                args = [chat]
            elif self.dt_begin.dateTime() == self.dt_end.dateTime():
                date = self.calendarWidget.selectedDate()
                date = f'{date.year()}-{str(date.month()).rjust(2, "0")}-{str(date.day()).rjust(2, "0")}%'
                query = f'''SELECT predicted_value, actual_value FROM PredictedMessage
                                WHERE actual_value IS NOT NULL AND chat_name LIKE ? AND
                                CONVERT(varchar(25), sending_date, 126) LIKE ?'''
                args = [chat, date]
            else:
                begin = self.dt_begin.dateTime().toString('yyyy-MM-ddThh:mm:ss')
                end = self.dt_end.dateTime().toString('yyyy-MM-ddThh:mm:ss')
                query = f'''SELECT predicted_value, actual_value FROM PredictedMessage
                                WHERE actual_value IS NOT NULL AND chat_name LIKE ? AND 
                                sending_date BETWEEN ? AND ?'''
                args = [chat, begin, end]
            data = np.array(self.answer_from_server(EXECUTE_QUERY, query=query, parse_date=True, args=args)[QUERY_RESULT])
            if len(data) > 0:
                y_test = [int(i['predicted_value']) for i in data]
                yhat = [int(i['actual_value']) for i in data]
            else:
                y_test = []
                yhat = []
            cnf_matrix = confusion_matrix(y_test, yhat, labels=[1, 0])
            np.set_printoptions(precision=2)
            self.sc.plot_confusion_matrix(cnf_matrix, classes=['Чрезвычайная ситуация', 'Обычные сообщения'], normalize=False,
                                  title='Матрица ошибок')
        # ЧС в конкретный день по часам
        elif self.dt_begin.dateTime() == self.dt_end.dateTime() and not self.check_all_date.isChecked():
            date = self.calendarWidget.selectedDate()
            date = f'{date.year()}-{str(date.month()).rjust(2, "0")}-{str(date.day()).rjust(2, "0")}%'
            query = f'''SELECT sending_date, predicted_value FROM PredictedMessage
                                        WHERE CONVERT(varchar(25), sending_date, 126) LIKE ? AND chat_name LIKE ?'''
            args = [date, chat]
            data = self.answer_from_server(EXECUTE_QUERY, query=query, args=args, parse_date=True)[QUERY_RESULT]
            result = {str(key).rjust(2, '0'): 0 for key in range(24)}
            print(data)
            for item in data:
                hour = item['sending_date'].split('T')[1].split(':')[0]
                result[hour] += item['predicted_value']
            self.sc.axes.plot(list(result.keys()), list(result.values()))
            self.sc.axes.set_title('Количество ЧС по часам', fontsize=12)
            self.sc.axes.set_xlabel('Часы', fontsize=10)
            self.sc.axes.set_ylabel('Количество ЧС', fontsize=10)
        # ЧС в диапазоне дат
        elif self.dt_begin.dateTime() != self.dt_end.dateTime() or self.check_all_date.isChecked():
            if self.check_all_date.isChecked():
                query = f'''SELECT sending_date, predicted_value FROM PredictedMessage
                                                        WHERE chat_name LIKE ?'''
                args = [chat]
            else:
                begin = self.dt_begin.dateTime().toString('yyyy-MM-ddThh:mm:ss')
                end = self.dt_end.dateTime().toString('yyyy-MM-ddThh:mm:ss')
                query = f'''SELECT sending_date, predicted_value FROM PredictedMessage
                                            WHERE chat_name LIKE ? and sending_date BETWEEN ? AND ?'''
                args = [chat, begin, end]
            data = self.answer_from_server(EXECUTE_QUERY, query=query, args=args, parse_date=True)[QUERY_RESULT]
            print(data)
            for item in data:
                date = item['sending_date'][:10]
                result[date] = result.get(date, 0) + item['predicted_value']
            self.sc.axes.bar(list(result.keys()), list(result.values()))
            self.sc.axes.set_title('Количество ЧС по дням', fontsize=12)
            self.sc.axes.set_xlabel('День', fontsize=10)
            self.sc.axes.set_ylabel('Количество ЧС', fontsize=10)
        self.sc.figure.tight_layout()
        self.layout_for_graph.addWidget(self.sc)
        self.sc.draw()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.notification.close_all()
        self.json_data['theme'] = 'white' if self.choice_theme.currentIndex() == 1 else 'black'
        self.json_data['hide_read'] = self.print_only_unread.isChecked()
        self.json_data['count_previous_message'] = self.count_context.value()
        if self.NBusually.isChecked():
            self.json_data['bayes'] = 'low'
        elif self.NBheavy.isChecked():
            self.json_data['bayes'] = 'heavy'
        else:
            self.json_data['bayes'] = 'medium'
        with open('../static/settings/setting.json', 'w') as file:
            json.dump(self.json_data, file)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_ADDRESS, SERVER_PORT))
    login = 'Petrov'
    password = hashlib.sha512('12345678Qq'.encode()).hexdigest()
    ex = Client(app, client_socket, login, '', app.styleSheet())
    answer = ex.answer_from_server(AUTH, args=[login, password])
    ex.show()
    ex.move(ex.width() + 1, ex.height() + 1)
    sys.excepthook = except_hook
    sys.exit(app.exec())
