#!python.exe
import os


def _get_article_html():
    """
    Чтение HTML-файла с шаблоном страницы демонстрации содержимого текстового файла.
    :return: Строка шаблона страницы демонстрации содержимого текстового файла
    """
    f = open(r'..\web\logs_page.html')
    return f.read()


def _get_response():
    """
    Построение ответа сервера на запрос.
    :return: Ответ сервера на запрос (страница или сообщение об ошибке)
    """
    html = _get_article_html()
    # Если файл существует
    if os.access('..\\..\\logs\\error.log', os.F_OK):
        log = open('..\\..\\logs\\error.log').read()
        return html.replace('{log}', log)
    else:
        return 'This file doesn\'t exist'


if __name__ == '__main__':
    # Построение ответа
    print('Content-type:text/html\r\n')
    print(_get_response())
