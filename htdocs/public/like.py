#!python.exe
import cgi
import requests

from view import write_log


def _get_printable_info():
    """
    Построение ответа сервера на запрос.
    :return: Ответ сервера на запрос
    """
    form = cgi.FieldStorage()
    article_id = form.getvalue('id')

    if not article_id or not article_id.isdigit():
        # Если аргумент ID не найден или не является числом
        write_log('LIKE INCREMENT - NO ID PROVIDED')
        return 'Please, input article ID into form parameters.'

    # Увеличение счёткиа полезности статьи
    resp = requests.post('http://127.0.0.1:8000/db/like_increment/' + article_id + '/')

    if resp.status_code == 200:
        # Если увеличение счётчика просмотров прошло успешно
        write_log('SUCCESSFUL LIKE INCREMENT - ID: ' + article_id)
        return 'Successful like counter increment'

    else:
        # Если увеличение счётчика полезности статьи не удалось
        write_log('LIKE INCREMENT ERROR - ID: ' + article_id)
        return resp.json()['detail']


if __name__ == '__main__':
    # Построение ответа
    print('Content-type:text/html\r\n')
    print(_get_printable_info())
