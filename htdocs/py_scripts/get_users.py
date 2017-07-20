#!python.exe
import json

import requests


def _get_printable_info():
    """
    Построение ответа сервера на запрос.
    :return: Ответ сервера на запрос
    """
    # Получение всех данных всех пользователей из базы данных
    resp = requests.get('http://127.0.0.1:8000/db/users/').json()

    # Построение словаря соответствия {'id': ('email', 'userID'), ...}
    users_dict = {}
    for user in resp:
        users_dict[str(user['id'])] = (user['email'], user['userID'])

    return json.dumps(users_dict)

if __name__ == '__main__':
    # Построение ответа
    print('Content-type:text/html\r\n\r\n')
    print(_get_printable_info())
