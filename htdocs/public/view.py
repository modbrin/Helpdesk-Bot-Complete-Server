#!python.exe
import datetime
import os
import sys

import cgi
import re  # regex
import requests


def write_log(text):
    """
    Запись действия в лог-файл.
    :param text: Текст для сохранения в лог-файле
    :return: None
    """
    if not os.access('..\\logs', os.F_OK):
        os.makedirs('..\\logs')
    log_file = open('..\\logs\\article_access.log', 'a')
    log_file.write(str(datetime.datetime.today()) + ' - ' + text + '\n')
    log_file.close()


def _get_article_html():
    """
    Чтение HTML-файла с шаблоном страницы статьи.
    :return: Строка шаблона страницы статьи
    """
    f = open('article.html')
    return f.read()


def _get_button_en():
    """
    Получение английского текста кнопки полезности статьи.
    :return: Текст кнопки
    """
    sys.path.append('..\\py_scripts')
    import db_defaults
    but_text = db_defaults.button_en()
    sys.path.append('..\\public')
    return but_text


def _get_button_ru():
    """
    Получение русского текста кнопки полезности статьи.
    :return: Текст кнопки
    """
    sys.path.append('..\\py_scripts')
    import db_defaults
    but_text = db_defaults.button_ru()
    sys.path.append('..\\public')
    return but_text


def _get_response():
    """
    Построение ответа сервера на запрос.
    :return: Ответ сервера на запрос (страница или сообщение об ошибке)
    """
    form = cgi.FieldStorage()
    article_id = form.getvalue('id')

    if not article_id or not article_id.isdigit():
        # Если аргумент ID не найден или не является числом
        write_log('NO ID PROVIDED')
        return 'Please, input article ID into form parameters.'

    # Получение статьи из базы данных
    resp = requests.get('http://127.0.0.1:8000/db/' + article_id + '/')
    if resp.status_code == 404:
        # Если статья не найдена
        write_log('ARTICLE NOT FOUND - ID: ' + article_id)
        return 'Article with ID ' + article_id + ' was not found.'

    article = resp.json()
    article_title = str(article['title'])
    article_text = str(article['text'])

    # Увеличение счёткиа просмотров
    resp = requests.post('http://127.0.0.1:8000/db/view_increment/' + article_id + '/')

    if resp.status_code != 200:
        # Если увеличение счётчика просмотров не удалось
        write_log('VIEW INCREMENT ERROR - ID: ' + article_id + '; ARTICLE: "' + article_title)
        return 'View increment error with code:' + str(resp.status_code) + ': ' + resp.json()['detail']

    # Запись в лог-файл
    write_log('SUCCESSFUL LOAD - ID: ' + article_id + '; ARTICLE: "' + article_title + '"')

    # Выбор языка для кнопки на странице
    if re.match(r'[а-яА-ЯёЁ]', article_title):
        button_text = _get_button_ru()
    else:
        button_text = _get_button_en()

    # Замена шаблонных полей на данные статьи
    article_html = _get_article_html()
    article_html = article_html.replace('{title}', article_title)
    article_html = article_html.replace('{text}', article_text)
    article_html = article_html.replace('{id}', article_id)
    article_html = article_html.replace('{button_text}', button_text)

    # Ответ страницей со статьёй
    return article_html

if __name__ == '__main__':
    # Построение ответа
    print('Content-type:text/html\r\n')
    print(_get_response())
