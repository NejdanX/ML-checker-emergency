from static.forms.login_form import Ui_LoginWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QIcon
from GUI.Constants import *
from math import ceil
import json
from GUI.MainWindow import Client
from GUI.Admin import UiClass
import sys
import socket
import hashlib
import threading
import traceback
import jwt
import time
# myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
# ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


def every(delay, task):
    """Every *delay seconds try to complete *task"""
    next_time = time.time() + delay
    while True:
        time.sleep(max(0, next_time - time.time()))
        try:
            task()
        except Exception:
            traceback.print_exc()
        # skip tasks if we are behind schedule:
        next_time += (time.time() - next_time) // delay * delay + delay


class Login(QMainWindow, Ui_LoginWindow):
    def __init__(self, app):
        super(Login, self).__init__()
        self.setupUi(self)
        self.app = app
        self.default_theme = self.app.styleSheet()
        self.server_available = False
        # create a client socket to connect to server
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.init_connection()
        self.initUI()

    def init_connection(self):
        self.try_connect()  # try to connect to server
        thread_connection = threading.Thread(target=every, args=(5, self.try_connect), daemon=True)
        # check server availability in a separate thread every 5 seconds
        thread_connection.start()

    def initUI(self):
        with open('../static/css/darkStyle.css') as file:
            app.setStyleSheet(file.read())
        self.setWindowIcon(QIcon("static/image/login_icon.png"))
        self.btn_sign_in.clicked.connect(self.sign_in)
        self.btn_sign_in.setProperty('class', 'big_button')
        self.input_login.setText('Petrov')
        self.input_password.setText('12345678Qq')

    def try_connect(self):
        """Makes a connection to the server if possible"""
        try:
            if not self.server_available:
                self.client_socket.connect((SERVER_ADDRESS, SERVER_PORT))
                self.statusBar().clearMessage()
                self.statusBar().setStyleSheet('color: green')
                self.statusBar().showMessage('Сервер доступен')
                self.btn_sign_in.setEnabled(True)
                self.server_available = True
        except Exception:
            self.server_is_not_available()

    def server_is_not_available(self):
        self.server_available = False
        self.statusBar().clearMessage()
        self.statusBar().setStyleSheet('color: red')
        self.statusBar().showMessage('Сервер недоступен. Вход невозможен')
        self.btn_sign_in.setEnabled(False)

    def sign_in(self):
        """User authorization and granting rights"""
        login = self.input_login.text()
        password = hashlib.sha512(self.input_password.text().encode()).hexdigest()
        try:
            answer = self.answer_from_server(AUTH, args=[login, password])  # send request to server
        except Exception:
            self.server_is_not_available()
            self.client_socket.close()
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            return
        if answer[STATUS]:
            role = jwt.decode(answer['token'], SECRET_KEY, algorithms='HS256')['role']
            id_employee = jwt.decode(answer['token'], SECRET_KEY, algorithms='HS256')['id_employee']
            full_name = jwt.decode(answer['token'], SECRET_KEY, algorithms='HS256')['full_name']
            if role == ADMIN:
                self.main_window = UiClass(self.app, self.client_socket, login.capitalize(),
                                           answer['token'], id_employee, self.default_theme)
            elif role == EXPERT:
                self.main_window = Client(self.app, self.client_socket, login.capitalize(),
                                          answer['token'], id_employee, full_name, self.default_theme)
            self.main_window.show()
            self.hide()
        else:
            self.statusBar().clearMessage()
            self.statusBar().setStyleSheet('color: red')
            self.statusBar().showMessage('Неверный логин или пароль')

    def answer_from_server(self, command, **kwargs):  # TODO do universal function
        """Get answer from server and parse that"""
        kwargs['command'] = command
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
        try:
            json_data = json.loads(answer)
            print(json_data)
            return json_data
        except Exception as e:
            print(e)
            return {STATUS: False, QUERY_RESULT: []}


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Login(app)
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())