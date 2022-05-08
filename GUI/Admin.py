from GUI.Constants import SERVER_ADDRESS
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QListWidgetItem, QHeaderView
from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QFileDialog, QAbstractItemView
from PyQt5 import QtGui
from static.forms.admin_form import Ui_MainWindow
from PyQt5.QtCore import Qt
from math import ceil
from static.forms.block_form import Ui_block_form
import sys
import json
from GUI.Constants import *
import datetime
import GUI.Password as Password
import hashlib


def transliterate(name):
    """Translates russian symbols into english to create a autologin"""
    dictionary = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
              'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
              'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
              'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
              'ю': 'u', 'я': 'ya', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'YO',
              'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
              'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H',
              'Ц': 'C', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH', 'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'E',
              'Ю': 'U', 'Я': 'YA'}
    result = ''
    for symbol in name:
        if symbol in dictionary:
            result += dictionary[symbol]
        else:
            result += symbol
    return result


class SettingServer(QMainWindow, Ui_MainWindow):
    def __init__(self, ui_class, client_socket):
        super(SettingServer, self).__init__()
        self.ui_class = ui_class
        self.setupUi(self)
        self.client_socket = client_socket
        self.initUI()
        # socket_thread = threading.Thread(target=wait_messages)
        # socket_thread.start()

    def initUI(self):
        self.ui_class.btn_save_copy.clicked.connect(self.query_for_backup)
        self.ui_class.btn_test.clicked.connect(self.test)
        self.get_all_chats()
        self.ui_class.combo_groups.currentIndexChanged.connect(self.change_group_for_analyze)
        self.ui_class.input_delete_time.editingFinished.connect(self.change_time_delete_non_disaster)
        self.ui_class.combo_units_delete.currentIndexChanged.connect(self.change_time_delete_non_disaster)
        self.radio_button_models = []
        self.ui_class.check_delete_non_disaster.clicked.connect(
            lambda: self.ui_class.combo_units_delete.setEnabled(self.ui_class.check_delete_non_disaster.isChecked()) or \
                    self.ui_class.input_delete_time.setEnabled(self.ui_class.check_delete_non_disaster.isChecked()) or \
                    self.ui_class.label_19.setEnabled(self.ui_class.check_delete_non_disaster.isChecked()))
        for i in range(self.ui_class.verticalLayout_5.count()):
            widget = self.ui_class.verticalLayout_5.itemAt(i).widget()
            if widget.__class__.__name__ == 'QRadioButton':
                widget.toggled.connect(self.change_model)
                self.radio_button_models.append(widget)

    def change_time_delete_non_disaster(self):
        answer = self.ui_class.answer_from_server('change_delete_time', time=self.ui_class.input_delete_time.value(),
                                         unit=self.ui_class.combo_units_delete.currentText())
        if not answer[STATUS]:
            message = f'Период удаления сообщений не изменен\n{answer[REASON]}'
            QMessageBox.warning(self.ui_class, answer[REASON], message, QMessageBox.Ok)

    def change_group_for_analyze(self):
        answer = self.ui_class.answer_from_server('analyze_group', group=self.sender().currentText())
        if not answer[STATUS]:
            message = f'Группы для анализа не изменены\n{answer[REASON]}'
            QMessageBox.warning(self.ui_class, answer[REASON], message, QMessageBox.Ok)

    def change_model(self):
        answer = {STATUS: False, QUERY_RESULT: 'Неизвестная ошибка'}
        for widget in self.radio_button_models:
            print(widget.objectName())
            if widget.isChecked():
                answer = self.ui_class.answer_from_server('change_model', file_name=widget.objectName())
                break
        if not answer[STATUS]:
            message = f'Строгость классификации не изменена\n{answer[REASON]}'
            QMessageBox.warning(self.ui_class, answer[REASON], message, QMessageBox.Ok)

    def test(self):
        message = self.ui_class.message_input.toPlainText()
        if not message:
            self.ui_class.result_window.addItem(QListWidgetItem('Текст не может быть пустым'))
            return
        data = self.ui_class.answer_from_server('test', message=message)
        if not data[STATUS]:
            data[QUERY_RESULT] = data[QUERY_RESULT] if data[QUERY_RESULT] else 'Недействительный JWT-токен'
            QMessageBox.warning(self.ui_class, 'Ошибка', data[REASON], QMessageBox.Ok)
            return
        answer, probability = data['answer'], data['probability']
        probability = 'Вероятность: ' + str(round(probability[1], 3))
        item = QListWidgetItem(message + '\n' + str(answer) + '\n' + probability)
        self.ui_class.result_window.clear()
        self.ui_class.result_window.addItem(item)

    def query_for_backup(self):
        answer = self.ui_class.answer_from_server('backup', path=self.ui_class.input_save_backup_path.text())
        if not answer[STATUS]:
            message = f'Резервная копия не создана\n{answer[REASON]}'
            QMessageBox.warning(self.ui_class, answer[REASON], message, QMessageBox.Ok)
        else:
            QMessageBox.information(self.ui_class, 'Успешно', 'Резервная копия успешно создана!', QMessageBox.Ok)

    def get_all_chats(self):
        query = 'SELECT DISTINCT chat_name FROM PredictedMessage'
        data = self.ui_class.answer_from_server(EXECUTE_QUERY, query=query, args=list())
        self.ui_class.combo_groups.clear()
        self.ui_class.combo_groups.addItem('Все')
        self.ui_class.combo_groups.addItems([item['chat_name'] for item in data[QUERY_RESULT]])


class SettingUsers(QMainWindow, Ui_MainWindow):
    def __init__(self, ui_class):
        super(SettingUsers, self).__init__()
        self.ui_class = ui_class
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.ui_class.btn_delete_user.clicked.connect(self.delete_user)
        self.ui_class.btn_disconnect_user.clicked.connect(self.disconnect_user)
        self.ui_class.btn_update.clicked.connect(lambda: self.get_all_active_user() or self.get_all_users())
        self.ui_class.btn_choice_log_path.clicked.connect(self.open_file_dialog)
        self.ui_class.btn_choice_backup_path.clicked.connect(self.open_file_dialog)
        self.ui_class.btn_create_user.clicked.connect(self.create_new_user)
        self.ui_class.input_full_name.editingFinished.connect(self.generate_login)
        self.ui_class.table_connection.itemSelectionChanged.connect(self.fill_user_info)
        self.ui_class.btn_commit_change.clicked.connect(self.update_user_info)
        self.get_all_active_user()
        self.setting_table()
        self.get_all_users()

    def fill_user_info(self):
        is_selected = bool(self.ui_class.table_connection.selectedItems())
        self.ui_class.tab_change_user.setEnabled(is_selected)
        if is_selected:
            cur_row = self.ui_class.table_connection.currentRow()
            cur_user_id = int(self.ui_class.table_connection.item(cur_row, 0).text())
            for user in self.all_users_information[QUERY_RESULT]:
                if cur_user_id == user['ID_employee']:
                    self.ui_class.input_full_name_change.setText(user['full_name'])
                    self.ui_class.input_username_change.setText(user['username'])
                    self.ui_class.phone_number_change.setText(user['phone_number'])
                    self.ui_class.combo_choice_role_change.setCurrentIndex(user['ID_role'] - 1)
        else:
            self.ui_class.input_full_name_change.clear()
            self.ui_class.input_username_change.clear()
            self.ui_class.input_password_change.clear()
            self.ui_class.input_repeat_password_change.clear()
            self.ui_class.phone_number_change.clear()

    def disconnect_user(self):
        cur_row = self.ui_class.table_connection.currentRow()
        username = self.ui_class.table_connection.item(cur_row, 1).text()
        answer = self.ui_class.answer_from_server('disconnect_user', username=username)
        if answer[STATUS]:
            self.ui_class.table_connection.setItem(cur_row, 2, QTableWidgetItem('Отсутствует'))
            self.ui_class.table_connection.setItem(cur_row, 3, QTableWidgetItem('Отключен'))
        self.get_all_active_user()
        self.get_all_users()
        if not answer[STATUS]:
            message = f'Пользователь не отключен\n{answer[REASON]}'
            QMessageBox.warning(self.ui_class, 'Ошибка', message, QMessageBox.Ok)

    def check_field_fill(self, full_name, username, phone_number, role, password, repeat_password):
        ok = True
        good_label_color = self.styleSheet()
        bad_label_color = 'color: red'
        good_labels = ['ФИО', 'Имя пользователя', 'Пароль', 'Номер телефона']
        bad_labels = ['ФИО должно быть заполнено', 'Имя пользователя должно быть заполнено',
                      'Пароль должен быть заполнен', 'Номер телефона должен быть заполнен']
        new_user_labels = [self.ui_class.lbl_full_name, self.ui_class.lbl_username,
                           self.ui_class.lbl_password, self.ui_class.lbl_phone_number]
        change_user_info_labels = [self.ui_class.lbl_full_name_change, self.ui_class.lbl_username_change,
                                   self.ui_class.lbl_password_change, self.ui_class.lbl_phone_number_change]
        params = [full_name, username, password, phone_number]
        if self.ui_class.tab_widget_user_info.currentIndex() == 1:
            is_password_ok = Password.check_password(self.ui_class.input_password_change.text())
            labels = change_user_info_labels
            if password is None:
                if repeat_password is None:
                    is_password_ok = 'ok'
                    del labels[2]
                    del good_labels[2]
                    del bad_labels[2]
                    del params[2]
                else:
                    labels[2].setText('Пароль: Пароли не совпадают')
                    labels[2].setStyleSheet(bad_label_color)
                    ok = False
        else:
            is_password_ok = Password.check_password(self.ui_class.input_password.text())
            labels = new_user_labels
        for index, item in enumerate(params):
            if not item:
                ok = False
                labels[index].setText(bad_labels[index])
                labels[index].setStyleSheet(bad_label_color)
            else:
                labels[index].setText(good_labels[index])
                labels[index].setStyleSheet(good_label_color)
        if password != repeat_password:
            labels[2].setText('Пароль: Пароли не совпадают')
            labels[2].setStyleSheet(bad_label_color)
            ok = False
        if is_password_ok != 'ok':
            labels[2].setText('Пароль: ' + is_password_ok)
            labels[2].setStyleSheet(bad_label_color)
            ok = False
        query_check_user = '''SELECT COUNT(username) FROM Employee
                                    WHERE username = ?'''
        user_already_in = self.ui_class.answer_from_server(EXECUTE_QUERY, query=query_check_user,
                                                           args=[username])
        if user_already_in[STATUS] and user_already_in[QUERY_RESULT][0]['COUNT(username)']:
            if self.ui_class.tab_widget_user_info.currentIndex() == 1 and \
                    username == self.ui_class.table_connection.item(self.ui_class.table_connection.currentRow(), 1).text():
                pass
            else:
                labels[1].setText('Имя пользователя: данное имя уже занято')
                labels[1].setStyleSheet(bad_label_color)
                ok = False
        return ok

    def create_new_user(self):
        full_name = self.ui_class.input_full_name.text()
        username = self.ui_class.input_username.text()
        password = self.ui_class.input_password.text()
        repeat_password = self.ui_class.input_repeat_password.text()
        phone_number = self.ui_class.phone_number.text()
        role_name = self.ui_class.combo_choice_role.currentText()
        if not self.check_field_fill(full_name, username, phone_number, role_name, password, repeat_password):
            return
        password = hashlib.sha512(self.ui_class.input_password.text().encode()).hexdigest()
        args = [full_name, username, password, phone_number, role_name]
        query = f'''INSERT INTO Employee(full_name, username, password_hash, phone_number, ID_role)
                    VALUES (?, ?, ?, ?, ?)'''
        answer = self.ui_class.answer_from_server(EXECUTE_QUERY, query=query, args=args)
        self.get_all_active_user()
        self.get_all_users()
        if not answer[STATUS]:
            message = f'Новый пользователь не добавлен\n{answer[REASON]}'
            QMessageBox.warning(self.ui_class, 'Ошибка', message, QMessageBox.Ok)

    def update_user_info(self):
        full_name = self.ui_class.input_full_name_change.text()
        username = self.ui_class.input_username_change.text()
        password = self.ui_class.input_password_change.text()
        repeat_password = self.ui_class.input_repeat_password_change.text()
        phone_number = self.ui_class.phone_number_change.text()
        role_name = self.ui_class.combo_choice_role_change.currentText()
        if not password:
            password = None
        if not repeat_password:
            repeat_password = None
        if not self.check_field_fill(full_name, username, phone_number, role_name, password, repeat_password):
            return
        cur_user_id = int(self.ui_class.table_connection.item(self.ui_class.table_connection.currentRow(), 0).text())
        if password:
            password = hashlib.sha512(self.ui_class.input_password_change.text().encode()).hexdigest()
            args = (full_name, username, phone_number, role_name, password, cur_user_id)
            query = f'''UPDATE Employee
                        SET full_name = ?, username = ?, phone_number = ?, ID_role = ?, password_hash = ?
                            WHERE ID_employee = ?'''
        else:
            args = (full_name, username, phone_number, role_name, cur_user_id)
            query = f'''UPDATE Employee
                        SET full_name = ?, username = ?, phone_number = ?, ID_role = ?
                            WHERE ID_employee = ?'''
        answer = self.ui_class.answer_from_server(EXECUTE_QUERY, query=query, args=args)
        if not answer[STATUS]:
            message = f'Данные о пользователе не обновлены\n{answer[REASON]}'
            QMessageBox.warning(self.ui_class, 'Ошибка', message, QMessageBox.Ok)

    def generate_login(self):
        full_name = self.ui_class.input_full_name.text().split()
        if full_name:
            login = transliterate(full_name[0])
            self.ui_class.input_username.setText(login)

    def open_file_dialog(self):
        if self.sender() == self.ui_class.btn_choice_backup_path:
            path = QFileDialog.getExistingDirectory(self)
            if path != self.ui_class.input_save_backup_path.text():
                pass # TODO
            self.ui_class.input_save_backup_path.setText(path)
        elif self.sender() == self.ui_class.btn_choice_log_path:
            path = QFileDialog.getExistingDirectory(self)
            self.ui_class.input_save_logs_path.setText(path)

    def delete_user(self):
        current_row = self.ui_class.table_connection.currentRow()
        if current_row == -1:
            return
        id_user = self.ui_class.table_connection.item(current_row, 0).text()
        username = self.ui_class.table_connection.item(current_row, 1).text()
        query = 'DELETE FROM Employee WHERE ID_employee = %s' % id_user
        reply = QMessageBox.question(self.ui_class, 'Подтверждение операции',
                                     'Вы уверены, что хотите удалить пользователя {}?'.format(username),
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            answer = self.ui_class.answer_from_server(EXECUTE_QUERY, query=query, args=list())
            if not answer[STATUS]:
                QMessageBox.warning(self.ui_class, 'Ошибка при удалении', answer[REASON],
                                    QMessageBox.Ok)
            else:
                self.get_all_users()
                self.get_all_active_user()

    def setting_table(self):
        self.header = ['ID', 'Имя пользователя', 'Текущий IP', 'Статус']
        self.ui_class.table_connection.setColumnCount(4)
        self.ui_class.table_connection.setHorizontalHeaderLabels(self.header)
        self.ui_class.table_connection.resizeColumnsToContents()
        self.ui_class.table_connection.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.ui_class.table_connection.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.ui_class.table_connection.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

    def get_all_users(self):
        query = 'SELECT DISTINCT * FROM Employee'
        self.all_users_information = self.ui_class.answer_from_server(EXECUTE_QUERY, query=query, args=list(), parse_date=True)
        data = [{key: value for key, value in user.items() if key in ['ID_employee', 'username', 'last_login_date', 'last_logout_date']}
                for user in self.all_users_information[QUERY_RESULT]]
        self.print_table(data)

    def get_all_active_user(self):
        self.active_users = self.ui_class.answer_from_server('active_users')
        if not self.active_users[STATUS]:
            message = f'Не удаётся получить список пользователей\n{self.active_users[REASON]}'
            QMessageBox.warning(self.ui_class, 'Ошибка', message, QMessageBox.Ok)

    def print_table(self, data):
        self.ui_class.table_connection.setRowCount(0)
        for i in range(len(data)):
            self.ui_class.table_connection.setRowCount(self.ui_class.table_connection.rowCount() + 1)
            for j, key in enumerate(data[i]):
                value = data[i][key]
                if j == 2:
                    value = self.active_users[QUERY_RESULT].get(data[i]['username'])
                    value = value if value else 'Отсутствует'
                if j == 3:
                    if data[i]['last_logout_date'] is not None and \
                            data[i]['last_login_date'] > data[i]['last_logout_date']:
                        value = 'Подключен'
                    else:
                        value = 'Отключен'
                item = QTableWidgetItem(str(value))
                self.ui_class.table_connection.setItem(self.ui_class.table_connection.rowCount() - 1, j, item)


class UiClass(QMainWindow, Ui_MainWindow):
    def __init__(self, app, client_socket, login, jwt_token, id_employee, default_theme):
        super(UiClass, self).__init__()
        self.setupUi(self)
        self.client_socket = client_socket
        self.app = app
        self.login = login
        self.id_employee = id_employee
        self.default_theme = default_theme
        self.jwt_token = jwt_token
        self.initUI()

    def initUI(self):
        self.table_connection.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tab_change_user.setEnabled(False)
        self.setting_users = SettingUsers(self)
        self.setting_server = SettingServer(self, self.client_socket)
        self.length_generate_password = 12
        self.setWindowTitle('Вы вошли как ' + self.login)
        self.setWindowIcon(QtGui.QIcon("../static/image/db_icon.png"))
        self.result_window.setWordWrap(True)
        self.date_begin_backup.setDateTime(datetime.datetime.now())
        self.btn_block_user.clicked.connect(self.open_block_window)
        self.check_scheduled_backup.clicked.connect(
            lambda: self.date_begin_backup.setEnabled(self.check_scheduled_backup.isChecked()) or
                    self.begin_backup_time.setEnabled(self.check_scheduled_backup.isChecked()) or
                    self.end_backup_time.setEnabled(self.check_scheduled_backup.isChecked()) or
                    self.combo_period_backup.setEnabled(self.check_scheduled_backup.isChecked()) or
                    self.btn_setting_backup_period.setEnabled(self.check_scheduled_backup.isChecked()) or
                    self.label_time_backup.setEnabled(self.check_scheduled_backup.isChecked()))

    def open_block_window(self):
        self.block_window = Block()
        self.block_window.show()

    def keyPressEvent(self, event):
        if self.main_tab_widget.currentIndex() != 1:
            return
        if self.tab_widget_user_info.currentIndex() == 0:
            password = self.input_password
            repeat_password = self.input_repeat_password
        else:
            password = self.input_password_change
            repeat_password = self.input_repeat_password_change
        if event.key() == Qt.Key_F1:  # Установка echoMode для пароля
            if password.echoMode() == password.Password:
                password.setEchoMode(password.Normal)
                repeat_password.setEchoMode(repeat_password.Normal)
            else:
                password.setEchoMode(password.Password)
                repeat_password.setEchoMode(repeat_password.Password)
        if event.key() == Qt.Key_F2:  # Случайно сгенерированный пароль
            new_password = Password.generate_password(self.length_generate_password)
            password.setText(new_password)
            repeat_password.setText(new_password)

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
            return {STATUS: 'False', QUERY_RESULT: []}
        message_length = ceil(int(message_length) / 1024)
        for i in range(message_length):
            answer += self.client_socket.recv(1024).decode('utf8')
        try:
            json_data = json.loads(answer)
            print(json_data)
            return json_data
        except Exception as e:
            print(e)
            return {STATUS: 'False', QUERY_RESULT: []}


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# def wait_messages():
#     while True:
#         data = client_socket.recv(1024)
#         if data:
#             print(data.decode())

class Block(QWidget, Ui_block_form):
    def __init__(self):
        super(Block, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon("static/image/login_icon.png"))


if __name__ == '__main__':
    server = (SERVER_ADDRESS, SERVER_PORT)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server)
    sys.excepthook = except_hook
    login = 'Ivanov'
    password = hashlib.sha512('12345678Qq'.encode()).hexdigest()
    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    with open('../static/css/darkStyle.css') as file:
        app.setStyleSheet(file.read())
    ui_class = UiClass(app, client_socket, login, '', app.styleSheet())
    answer = ui_class.answer_from_server(AUTH, args=[login, password])
    ui_class.show()
    sys.exit(app.exec())
