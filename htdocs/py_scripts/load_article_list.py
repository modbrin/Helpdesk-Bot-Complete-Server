#!python.exe
import json

import requests


def _get_printable_info():
    """
    Построение ответа сервера на запрос.
    :return: Ответ сервера на запрос
    """
    # Получение всех данных всех статей из базы данных
    resp = requests.get('http://127.0.0.1:8000/db/').json()

    # Построение словаря соответствия {'id': 'title', ...}
    article_dict = {}
    for article in resp:
        article_dict[str(article['id'])] = article['title']

    return json.dumps(article_dict)

if __name__ == '__main__':
    # Построение ответа
    print('Content-type:text/html\r\n\r\n')
    print(_get_printable_info())
