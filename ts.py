from GUI import preprocessing
import threading
import telebot
from datetime import datetime
from work_with_db import Sql
import time
import os
import sys
from GUI.Constants import *
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import failure, connectionDone
from twisted.internet import reactor, task
import pandas as pd
import jwt
import json
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from env.token import TG_TOKEN
bot = telebot.TeleBot(TG_TOKEN)
info = ''

# def benchmark(jwt_token={}, query={}):
#     def logger(func):
#         """
#         Логи представлены в виде:
#         дата время:функция:(id работника:ФИО:роли) или (Unauthorized):запрос:успех запроса:причина не успеха
#         """
#         def wrapper(*args, **kwargs):
#             if jwt_token:
#                 role = jwt.decode(jwt_token['token'], SECRET_KEY, algorithms='HS256')['role']
#                 id_employee = jwt.decode(jwt_token['token'], SECRET_KEY, algorithms='HS256')['id_employee']
#                 full_name = jwt.decode(jwt_token['token'], SECRET_KEY, algorithms='HS256')['full_name']
#                 info = [id_employee, full_name, role]
#             else:
#                 info = ['Unauthorized']
#             string = f'{datetime.now().strftime(DATE_FORMAT)}func.__class__.name:{":".join(info)}'
#             if query:
#                 string += f':{query["text"]}:{query[STATUS]}'
#                 if not query[STATUS]:
#                     string += ':' + query[REASON]
#             with open('../static/logs/logs.txt', 'a', encoding='utf8') as file:
#                 file.write(string)
#             func(*args, **kwargs)
#         return wrapper
#     return logger


class ThreadSafeDict(dict):
    def __init__(self, * p_arg, ** n_arg):
        dict.__init__(self, * p_arg, ** n_arg)
        self._lock = threading.Lock()

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, type, value, traceback):
        self._lock.release()


class ProcessClient(LineReceiver):
    def __init__(self, server, addr):
        self.connection = Sql(DB_FILE_NAME)
        self.addr = addr
        self.server = server

    def connectionMade(self):
        print(f'New connection')
        self.server.concurrent_count_client += 1

    def dataReceived(self, data):
        try:
            print(data.decode('utf8').replace("'", '"'))
            json_data = json.loads(data.decode('utf8').replace("'", '"'))
        except Exception as e:
            print(e)
            send = json.dumps({STATUS: False, QUERY_RESULT: [], REASON: 'Невозможно обработать запрос'})
            self.send_count_bytes(send)
            self.sendLine(send.encode())
            return
        try:
            if json_data['command'] == 'auth':
                self.auth(json_data)
                return
            if not json_data['jwt_token']:
                send = json.dumps({STATUS: False, QUERY_RESULT: [], REASON: 'Недействительный JWT-токен'})
                self.send_count_bytes(send)
                self.sendLine(send.encode())
                return
            info = jwt.decode(json_data['jwt_token'], SECRET_KEY, algorithms='HS256')
            if not self.server.clients.get(info.get('login')):
                send = json.dumps({STATUS: False, QUERY_RESULT: [], REASON: 'Недействительный JWT-токен'})
                self.send_count_bytes(send)
                self.sendLine(send.encode())
                return
            if json_data['command'] == 'DB_data':
                self.execute_query(json_data)
            elif json_data['command'] == 'backup':
                self.backup(json_data)
            elif json_data['command'] == 'test':
                answer, probability = self.server.make_prediction(json_data['message'])
                send = json.dumps({STATUS: True, "answer": answer,
                                   "probability": [probability[0], probability[1]]})
                self.send_count_bytes(send)
                self.sendLine(send.encode())
            elif json_data['command'] == 'active_users':
                clients = {key: value[0] for key, value in self.server.clients.items()}
                send = json.dumps({STATUS: True, QUERY_RESULT: clients})
                self.send_count_bytes(send)
                self.sendLine(send.encode())
            elif json_data['command'] == 'change_model':
                with open(f'static/models/{json_data["file_name"]}_model.pkl', 'rb') as file:
                    self.server.classifier = pickle.load(file)
                send = json.dumps({STATUS: True})
                self.send_count_bytes(send)
                self.sendLine(send.encode())
            elif json_data['command'] == 'analyze_group':
                self.server.analyze_group = json_data['group']
                send = json.dumps({STATUS: True})
                self.send_count_bytes(send)
                self.sendLine(send.encode())
            elif json_data['command'] == 'change_delete_time':
                self.server.delete_time = json_data['time'] * TIME_UNIT_IN_SECONDS[json_data['unit']]
                send = json.dumps({STATUS: True})
                self.send_count_bytes(send)
                self.sendLine(send.encode())
            elif json_data['command'] == 'get_new_disaster_message':
                self.get_new_disaster_message()
            elif json_data['command'] == 'disconnect_user':
                send = json.dumps({STATUS: True})
                self.connectionLost(dis_username=json_data['username'])
                self.send_count_bytes(send)
                self.sendLine(send.encode())
            else:
                send = json.dumps({STATUS: False, QUERY_RESULT: [], REASON: "Неизвестная команда"})
                self.send_count_bytes(send)
                self.sendLine(send.encode())
        except Exception as e:
            send = json.dumps({STATUS: False, QUERY_RESULT: [], REASON: "Ошибка сервера"})
            print(e)
            self.send_count_bytes(send)
            self.sendLine(send.encode())

    def get_new_disaster_message(self):
        if self.username in self.server.unread_messages:
            if self.server.unread_messages['Not determined']:
                message = self.server.unread_messages['Not determined'].pop(0)
                self.server.unread_messages[self.username].append(message)
            if not self.server.unread_messages[self.username]:
                send = json.dumps({STATUS: True, QUERY_RESULT: []})
                self.send_count_bytes(send)
                self.sendLine(send.encode())
                return
            cur = self.connection.cursor()
            ids = [id_mes['ID_message'] for id_mes in self.server.unread_messages[self.username]]
            placeholder = '?'
            placeholders = ', '.join([placeholder] * len(ids))
            query = f'''UPDATE PredictedMessage 
                        SET ID_employee = {self.id_employee}
                            WHERE id_message IN (%s)''' % placeholders
            cur.execute(query, ids)
            self.parse_date_for_json(self.server.unread_messages[self.username])
            send = json.dumps({STATUS: True, QUERY_RESULT: self.server.unread_messages[self.username]})
            self.connection.cnxn.commit()
            self.send_count_bytes(send)
            self.sendLine(send.encode())
            self.server.unread_messages[self.username].clear()
        else:
            send = json.dumps({STATUS: False, QUERY_RESULT: [], REASON: 'Пользователь не найден/сообщений нет'})
            self.send_count_bytes(send)
            self.sendLine(send.encode())

    def execute_query(self, data):
        cur = self.connection.cursor()
        try:
            if data['query'].startswith('SELECT'):
                self.select_data(data, cur)
            elif data['query'].startswith('UPDATE'):
                self.update_data(data, cur)
            elif data['query'].startswith('DELETE'):
                self.delete_user(data, cur)
            elif data['query'].startswith('INSERT'):
                self.insert_user(data, cur)
        except Exception as e:
            print(e)
            send = json.dumps({STATUS: False, QUERY_RESULT: [], REASON: 'Невозможно выполнить запрос'})
            self.send_count_bytes(send)
            self.sendLine(send.encode())
            return

    def insert_user(self, data, cur):
        role_id = cur.execute(f'''SELECT ID_role FROM Role
                                        WHERE name = ?''', (data['args'][-1])).fetchone()[0]
        data['args'][-1] = role_id
        cur.execute(data['query'], tuple(data['args']))
        self.connection.cnxn.commit()
        id_inserted_client = cur.execute(f'''SELECT ID_employee FROM Employee 
                                                WHERE ID_employee = (SELECT IDENT_CURRENT('Employee'))''').fetchone()
        self.server.employee_ids.append(id_inserted_client[0])
        send = json.dumps({STATUS: True, QUERY_RESULT: []})
        self.send_count_bytes(send)
        self.sendLine(send.encode())

    def delete_user(self, data, cur):
        try:
            cur.execute(data['query'])
            self.connection.cnxn.commit()
        except Exception as e:
            message = "Не удалось удалить пользователя, так как на него ссылаются из других таблиц"
            send = json.dumps({STATUS: False, QUERY_RESULT: [], REASON: message})
            self.send_count_bytes(send)
            self.sendLine(send.encode())
            return
        send = json.dumps({STATUS: True, QUERY_RESULT: []})
        self.send_count_bytes(send)
        self.sendLine(send.encode())

    def backup(self, json_data):
        cur = self.connection.cursor()
        path = json_data['path']
        if not os.path.isdir(path):
            send = json.dumps({STATUS: False, QUERY_RESULT: [], REASON: "Указанный путь не найден"})
            self.send_count_bytes(send)
            self.sendLine(send.encode())
            return
        date = datetime.now().strftime('%Y-%m-%dT%H.%M.%S')
        cur.execute(f"BACKUP DATABASE DUI TO DISK='{path}/DUI{date}.bak' with FORMAT")
        while cur.nextset():
            pass
        send = json.dumps({STATUS: True, QUERY_RESULT: []})
        self.send_count_bytes(send)
        self.sendLine(send.encode())

    def update_data(self, data, cur):
        self.check_on_none(data)
        if 'ID_role' in data['query']:
            data['args'][3] = cur.execute(f'''SELECT ID_role FROM Role
                                        WHERE name = ?''', (data['args'][3],)).fetchone()[0]
        cur.execute(data['query'], tuple(data['args']))
        self.connection.cnxn.commit()
        send = json.dumps({STATUS: True, QUERY_RESULT: []})
        self.send_count_bytes(send)
        self.sendLine(send.encode())

    def check_on_none(self, data):
        if 'None' in data['args']:
            for i in range(len(data['args'])):
                if data['args'][i] == 'None':
                    data['args'][i] = None

    def select_data(self, data, cur):
        temp = data['query'][7:].replace('DISTINCT ', '').split(' FROM')
        self.check_on_none(data)
        table_name = temp[1].split()[0].strip()
        if '*' in temp[0]:
            column_names = [row.column_name for row in cur.columns(table=table_name)]
        else:
            column_names = temp[0].split(', ')
        query_result = cur.execute(data['query'], tuple(data['args'])).fetchall()
        query_result = list(map(list, query_result))
        new_data = [dict(zip(column_names, row)) for row in query_result]
        if data.get('parse_date'):
            self.parse_date_for_json(new_data)
        send = json.dumps({STATUS: True, QUERY_RESULT: new_data})
        self.send_count_bytes(send)
        self.sendLine(send.encode())

    def parse_date_for_json(self, new_data):
        for item in new_data:
            for key in item.keys():
                if 'date' in key:
                    item[key] = item[key].strftime(DATE_FORMAT) if item[key] is not None else None

    def send_count_bytes(self, data):
        count_bytes = str(sys.getsizeof(data)).rjust(11, '0')
        self.sendLine(json.dumps({'count_bytes': count_bytes}).encode())

    def auth(self, data):
        cur = self.connection.cursor()
        try:
            login, password = data['args']
        except Exception as e:
            print(e)
            send = json.dumps({STATUS: False, QUERY_RESULT: [], REASON: "Плохие данные для авторизации"})
            self.send_count_bytes(send)
            self.sendLine(send.encode())
            return
        is_correct_user = cur.execute('''
                                SELECT ID_employee, username, full_name, ID_role FROM Employee
                                    WHERE username = ? AND password_hash = ?''',
                                      (login, password)).fetchall()
        if is_correct_user and is_correct_user[0][0]:
            role = cur.execute('''SELECT name FROM Role WHERE ID_role = ?''', (is_correct_user[0][3],)).fetchone()[0]
            self.id_employee = is_correct_user[0][0]
            full_name = is_correct_user[0][2]
            self.username = login
            cur.execute('''UPDATE Employee
                           SET last_login_date = ?
                               WHERE username = ?''', (datetime.now(), login))
            self.jwt_token = self.get_jwt_token(login, full_name, role)
            self.server.clients[login] = [self.addr.host, self.jwt_token]
            self.server.unread_messages[self.username] = []
            send = json.dumps({STATUS: True, "token": self.jwt_token})
            self.send_count_bytes(send)
            self.sendLine(send.encode())
        else:
            send = json.dumps({STATUS: False, QUERY_RESULT: [], REASON: 'Пользователь не найден'})
            self.send_count_bytes(send)
            self.sendLine(send.encode())

    def get_jwt_token(self, login, full_name, role):
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {"id_employee": self.id_employee, "login": login, "full_name": full_name, "role": role}
        encoded = jwt.encode(payload, SECRET_KEY, algorithm="HS256", headers=header)
        return encoded

    def connectionLost(self, dis_username='', reason: failure.Failure = connectionDone):
        cur = self.connection.cursor()
        lost = 'Пользователь подключился, но не прошёл авторизацию'
        if dis_username:
            if not self.server.clients.get(dis_username):
                return
            else:
                self.do_con_lost(cur, dis_username)
        else:
            if not self.server.clients.get(self.username):
                return
            else:
                self.do_con_lost(cur, dis_username)
        print(f'Lost connection')

    def do_con_lost(self, cur, username):
        cur.execute('''UPDATE Employee
                       SET last_logout_date = ?
                           WHERE username = ?''', (datetime.now(), username))
        self.server.clients.pop(username)
        rest = self.server.unread_messages.get(username)
        if rest:
            self.server.unread_messages['Not determined'] += rest
        del self.server.unread_messages[username]
        self.server.concurrent_count_client -= 1
        self.server.current_to_sending_client -= 1
        if self.server.current_to_sending_client < 0:
            self.server.current_to_sending_client = 0


class Server(Factory):
    commands = {'init', 'send', 'get', 'close'}

    def __init__(self):
        self.concurrent_count_client = 0
        self.connection = Sql(DB_FILE_NAME)
        self.analyze_group = 'Все'
        self.delete_time = 0
        self.backup_time = 0
        delete_disaster = task.LoopingCall(self.delete_non_disaster_from_db)
        delete_disaster.start(self.delete_time)
        self.current_client_for_non_disaster_message = 0
        self.unread_messages = ThreadSafeDict()
        self.employee_ids = self.connection.cursor().execute('SELECT ID_employee FROM Employee').fetchall()
        self.employee_ids = [item[0] for item in self.employee_ids]
        self.employee_ids.remove(7)
        self.employee_ids.remove(13)
        print(self.employee_ids)
        self.unread_messages['Not determined'] = []
        self.current_to_sending_client = 0
        self.clients = {}

    def delete_non_disaster_from_db(self):
        if self.delete_time == 0:
            return
        cur = self.connection.cursor()
        print(self.delete_time)
        dates = cur.execute('''SELECT id_message, sending_date FROM PredictedMessage
                                   WHERE predicted_value = 0 OR actual_value = 0''').fetchall()
        ids = tuple(date[0] for date in dates if (datetime.now() - date[1]).total_seconds() > self.delete_time)
        if len(ids):
            placeholder = '?'
            placeholders = ', '.join([placeholder] * len(ids))
            query = f'''DELETE FROM PredictedMessage WHERE id_message IN (%s)''' % placeholders
            cur.execute(query, ids)
            self.connection.cnxn.commit()

    def auto_delete(self):
        self.thread_delete = threading.Thread(target=self.delete_non_disaster_from_db)
        self.thread_delete.run()

    def buildProtocol(self, addr):
        return ProcessClient(self, addr)

    def open_model(self):
        with open(f'static/models/NBnormal_model.pkl', 'rb') as file:
            self.classifier = pickle.load(file)
        self.vectorizer = TfidfVectorizer()
        train = pd.read_csv('Proccesing_data/clear_train.csv')
        self.vectorizer.fit_transform(train['cleared_text'])

    def make_prediction(self, message):
        """Возвращает предсказанный класс и вероятность для введенного сообщения"""
        clear_message = preprocessing.clear_message(message)
        print(clear_message)
        answer = str(self.classifier.predict(self.vectorizer.transform([clear_message]))[0])
        answer = 'ЧС подтверждена' if answer == '1' else 'ЧС не подтверждена'
        probability = self.classifier.predict_proba(self.vectorizer.transform([clear_message]))
        print(probability)
        return answer, probability[0]

    def react(self, info, message):
        answer, probability = self.make_prediction(message)
        disaster = 1 if answer == 'ЧС подтверждена' else 0
        new_connection = Sql(DB_FILE_NAME)
        cur = new_connection.cursor()
        data = (info['message'], info['chat_name'], info['chat_type'], info['sender'].strip(), info['date'],
                round(probability[1], 3), disaster, 13)
        info['predicted_value'] = disaster
        info['probability'] = round(probability[1], 3)
        cur.execute(f'''INSERT INTO PredictedMessage(message_text, chat_name, chat_type, sender, sending_date, 
                            probability, predicted_value, ID_employee) VALUES {data}''')
        self.connection.cnxn.commit()
        new_data = cur.execute(f'''SELECT * FROM PredictedMessage
                                WHERE ID_message = (SELECT IDENT_CURRENT('PredictedMessage'))''').fetchone()
        column_names = [row.column_name for row in cur.columns(table='PredictedMessage')]
        new_data = dict(zip(column_names, list(new_data)))
        if new_data['probability'] < 0.5:
            cur.execute(f'''UPDATE PredictedMessage
                            SET ID_employee = ?
                                WHERE ID_message = ?''', (self.employee_ids[self.current_client_for_non_disaster_message],
                                                          new_data['ID_message']))
            self.current_client_for_non_disaster_message += 1
            self.current_client_for_non_disaster_message %= len(self.employee_ids)
        print(self.current_to_sending_client)
        if new_data['probability'] >= 0.5:
            with self.unread_messages as ms:
                koef = 0
                keys = list(self.clients.keys())
                for admin in ADMINS:
                    if admin in self.clients.keys():
                        keys.remove(admin)
                        koef += 1
                if not self.concurrent_count_client:
                    ms['Not determined'].append(new_data)
                    return
                key = keys[self.current_to_sending_client]
                if key in ms:
                    ms[key].append(new_data)
                else:
                    ms[key] = [new_data]
                self.current_to_sending_client = (self.current_to_sending_client + 1) % (self.concurrent_count_client - koef)


def handle_data(message):
    if message.chat.type == 'group':
        chat_type = 'Группа'
        chat_name = message.chat.title
    elif message.chat.type == 'private':
        chat_type = 'Личные сообщения'
        chat_name = message.chat.username
    else:
        chat_type = 'Не определен'
        chat_name = 'Имя чата не определено'
    date = datetime.utcfromtimestamp(int(message.date) + 60 * 60 * 9).strftime('%Y-%m-%dT%H:%M:%S')
    sender = message.from_user
    sender = f'{"BOT" if sender.is_bot else ""} {sender.first_name} {sender.last_name}({sender.username})'
    result = {
        "chat_name": chat_name,
        "chat_type": chat_type,
        "date": date,
        "sender": sender,
        'message': message.text
    }
    return result


@bot.message_handler(func=lambda x: True)
def get_message(message):
    time.sleep(0.5)
    info = handle_data(message)
    print(info['chat_name'] not in obj.analyze_group or obj.analyze_group != 'Все')
    if info['chat_name'] not in obj.analyze_group and obj.analyze_group != 'Все':
        return
    obj.react(info, message.text)


if __name__ == '__main__':
    obj = Server()
    obj.open_model()
    obj.auto_delete()
    reactor.listenTCP(SERVER_PORT, obj)
    first = threading.Thread(target=bot.polling, kwargs={'none_stop': True}, daemon=True)
    first.start()
    print('Server OK')
    reactor.run()
