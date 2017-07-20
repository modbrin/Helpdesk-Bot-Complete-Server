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
    article_id = form.getvalue('id')

    # Если ID статьи не был дан или не является числом
    if not article_id or not article_id.isdigit():
        return dict(detail='ID is required')

    # Получение данных из полей формы
    article = {}
    for param in form.list:
        article[param.name] = param.value

    # Попытка обновления статьи в базе данных
    resp = requests.put('http://127.0.0.1:8000/db/' + article_id + '/', data=article, auth=get_auth_data())

    # Если операция прошла неуспешно
    if resp.status_code != 200:
        return resp.json()

    return {}

if __name__ == '__main__':
    # Построение ответа
    print('Content-type:text/html\r\n\r\n')
    print(json.dumps(_get_printable_info()))
