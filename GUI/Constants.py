import socket


SORT_COLUMN = {
    'Названию чата': 'chat_name',
    'Отправителю': 'sender',
    'Дате': 'sending_date',
    'Вероятности': 'probability'
}
DB_FILE_NAME = 'DUI'
EXECUTE_QUERY = 'DB_data'
STATUS = 'Status'
QUERY_RESULT = 'Query_result'
REASON = 'Reason'
AUTH = 'auth'
ADMIN = 'Admin'
EXPERT = 'Expert'
SECRET_KEY = 'NejdanX'
ADMINS = ['Ivanov', 'Unknown']
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'
SERVER_PORT = 9090
POLLING_RATE = 5
SERVER_ADDRESS = socket.gethostbyname(socket.gethostname())
TIME_UNIT_IN_SECONDS = {
    'Минут': 60,
    'Часов': 60 * 60,
    'Дней': 60 * 60 * 24,
    'Месяцев': 60 * 60 * 24 * 30,
    'Лет': 60 * 60 * 24 * 365
}
