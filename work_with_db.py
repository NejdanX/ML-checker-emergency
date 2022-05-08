import pyodbc
from datetime import datetime


class Sql:
    def __init__(self, database, server='GP-PC\\MSSQLSERVERNOTE'):
        self.cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                                   "Server=" + server + ";"
                                   "Database=" + database + ";"
                                   "Trusted_Connection=yes;",
                                   autocommit=True)
        self.query = "-- {}\n\n-- Made in Python".format(datetime.now()
                                                         .strftime("%d/%m/%Y"))

    def cursor(self):
        return self.cnxn.cursor()


if __name__ == '__main__':
    pass
    # print(datetime.now())
    # s = Sql('DUI')
    # data = {'query': f'''UPDATE PredictedMessage
    #                         SET actual_value = ?
    #                         WHERE ID_message = ?''', 'args': [1, 10]}
    #
    # s.cursor().execute(data['query'], tuple(data['args']))
    # s.cnxn.commit()





