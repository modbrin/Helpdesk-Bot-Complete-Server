#!python.exe
import json

import requests


def _get_printable_info():
    """
    Построение ответа сервера на запрос.
    :return: Ответ сервера на запрос
    """
    # Получение всех данных всех сообщений обратной связи из базы данных
    resp = requests.get('http://127.0.0.1:8000/db/feedback/').json()

    # Построение словаря соответствия {'id': ('name', 'email', 'grade', 'text'), ...}
    feedback_dict = {}
    for feedback in resp:
        feedback_dict[str(feedback['id'])] = (feedback['name'], feedback['email'],
                                              str(feedback['grade']), feedback['text'])

    return json.dumps(feedback_dict)

if __name__ == '__main__':
    # Построение ответа
    print('Content-type:text/html\r\n\r\n')
    print(_get_printable_info())
