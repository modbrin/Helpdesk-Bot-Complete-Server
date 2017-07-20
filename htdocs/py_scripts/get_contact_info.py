#!python.exe
import json

import requests


def _get_printable_info():
    """
    Построение ответа сервера на запрос.
    :return: Ответ сервера на запрос
    """
    # Получение строки с контактными данными из базы данных
    resp = requests.get('http://127.0.0.1:8000/db/contact_info/')
    # Если получены верные данные (массив, состоящий из словаря, содержащего только поле 'info')
    if len(resp.json()) > 0:
        return resp.json()[0]
    # В случае ошибки получения данных вернуть текст ошибки
    return dict(detail='No contact info stored in the DB')

if __name__ == '__main__':
    # Построение ответа
    print('Content-type:text/html\r\n\r\n')
    print(json.dumps(_get_printable_info()))
