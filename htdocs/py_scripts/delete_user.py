#!python.exe
import cgi
import json

import requests

from db_defaults import get_auth_data


def _get_printable_info():
    """
    Построение ответа сервера на запрос.
    :return: Ответ сервера на запрос
    """
    form = cgi.FieldStorage()
    user_id = form.getvalue('id')

    # Удаление пользователя из базы данных
    resp = requests.delete('http://127.0.0.1:8000/db/users/' + user_id + '/', auth=get_auth_data())

    # Если операция прошла неуспешно
    if resp.status_code != 204:
        return resp.json()

    return {}

if __name__ == '__main__':
    # Построение ответа
    print('Content-type:text/html\r\n\r\n')
    print(json.dumps(_get_printable_info()))
