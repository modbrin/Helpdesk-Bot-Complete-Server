#!python.exe
import json

import requests

from db_defaults import get_auth_data, def_user


def _get_printable_info():
    """
    Построение ответа сервера на запрос.
    :return: Ответ сервера на запрос
    """
    # Инициализация словаря с данными по-умолчанию
    def_dict = dict(email=def_user(),
                    activationKey='None')

    # Попытка создания пользователя в базе данных
    resp = requests.post('http://127.0.0.1:8000/db/users/', data=def_dict, auth=get_auth_data())
    result = resp.json()

    # Если создание пользователя в базе данных не удалось
    if resp.status_code != 200:
        return result

    # В случае успеха возвращаем ID нового пользователя в базе данных
    return dict(id=result['id'])

if __name__ == '__main__':
    # Построение ответа
    print('Content-type:text/html\r\n\r\n')
    print(json.dumps(_get_printable_info()))
