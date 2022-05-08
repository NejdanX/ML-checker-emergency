from static.forms.report_form import Ui_report_form
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from docxtpl import DocxTemplate
import sys


class Report(QWidget, Ui_report_form):
    # Generate a disaster report based on a template
    def __init__(self, employee_name, data_about_message):
        super(Report, self).__init__()
        self.setupUi(self)
        self.doc = DocxTemplate('../static/docs/Template.docx')
        self.data_about_message = data_about_message
        self.setWindowTitle(f'Отчёт о сообщение {data_about_message["ID_message"]}')
        self.full_name = employee_name
        self.predicted_answer = self.data_about_message['predicted_value']
        self.predicted_answer = 'Сообщение является ЧС' if self.predicted_answer else 'Сообщение не является ЧС'
        self.actual_answer = self.data_about_message['actual_value']
        if self.actual_answer is None:
            self.actual_answer = 'Нет данных'
        elif self.actual_answer:
            self.actual_answer = 'Сообщение является ЧС'
        else:
            self.actual_answer = 'Сообщение не является ЧС'
        self.fill_field()
        self.btn_create_filled_report.clicked.connect(self.document_one_message)

    def fill_field(self):
        self.id_message.setText(str(self.data_about_message['ID_message']))
        self.receive_date.setText(self.data_about_message['sending_date'].replace('T', ' '))
        self.sender_message.setText(self.data_about_message['sender'])
        self.source.setText(self.data_about_message['chat_name'])
        self.predicted.setText(self.predicted_answer)
        self.actual.setText(self.actual_answer)

    def document_one_message(self):
        full_name = self.full_name
        ID = self.data_about_message['ID_message']
        initials = full_name.split()
        initials = f'{initials[0]} {initials[1][0]}.{initials[2][0]}.'
        sender = self.data_about_message['sender']
        sending_date = self.data_about_message['sending_date'].replace('T', ' ')
        chat = self.data_about_message['chat_name']
        emergency_class = self.emergency_class.currentText()
        emergency_types = self.emergency_type.currentText()
        about_event = self.emergency_description.toPlainText()
        emergency_scale = self.impact_and_scale.toPlainText()
        operator_actions = self.operator_actions.toPlainText()
        context = {
            'emergency_id': str(ID),
            'employee': full_name,
            'sending_date': sending_date,
            'sender': sender,
            'chat_name': chat,
            'predicted_value': self.predicted_answer,
            'actual_value': self.actual_answer,
            'emergency_class': emergency_class,
            'emergency_types': emergency_types,
            'about_event': about_event,
            'emergency_scale': emergency_scale,
            'person_action': operator_actions,
            'extra_information': '',
            'employee_initials': initials
        }
        self.doc.render(context)
        self.doc.save(f'../static/docs/Отчёт ЧС {ID}.docx')
        QMessageBox.information(self, 'Успешно', 'Отчёт успешно сохранен', QMessageBox.Ok)
        self.close()


def russian_name_month(name):
    MONTH = {
        'January': 'января',
        'February': 'февраля',
        'March': 'марта',
        'April': 'апреля',
        'May': 'мая',
        'June': 'июня',
        'July': 'июля',
        'August': 'августа',
        'September': 'сентября',
        'October': 'октября',
        'November': 'ноября',
        'December': 'декабря'
    }
    return MONTH[name]


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Report([])
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
