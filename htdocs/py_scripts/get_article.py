#!python.exe
import cgi
import json

import requests


def _get_printable_info():
    """
    Построение ответа сервера на запрос.
    :return: Ответ сервера на запрос
    """
    form = cgi.FieldStorage()
    article_id = form.getvalue('id')

    # Если ID не предоставлен или не является числом
    if not article_id or not article_id.isdigit():
        return dict(detail='ID is required')

    # Попытка получения статьи из базы данных
    resp = requests.get('http://127.0.0.1:8000/db/' + article_id + '/')

    # Передача полученных данных
    return json.dumps(resp.json())

if __name__ == '__main__':
    # Построение ответа
    print('Content-type:text/html\r\n\r\n')
    print(_get_printable_info())
