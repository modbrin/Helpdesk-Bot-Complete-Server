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

    # Если ID пользователя не был дан или не является числом
    if not user_id or not user_id.isdigit():
        return dict(detail='ID is required')

    # Получение данных из полей формы
    user = {}
    for param in form.list:
        user[param.name] = param.value

    # Попытка обновления данных пользователя в базе данных
    resp = requests.put('http://127.0.0.1:8000/db/users/' + user['id'] + '/', data=user, auth=get_auth_data())

    # Если операция прошла неуспешно
    if resp.status_code != 200:
        return resp.json()

    return {}

if __name__ == '__main__':
    # Построение ответа
    print('Content-type:text/html\r\n\r\n')
    print(json.dumps(_get_printable_info()))
