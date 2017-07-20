#!python.exe
import cgi
import os

import re
import requests
import shutil

from db_defaults import get_auth_data, def_mail_domain


def save_uploaded_file(upload_dir, form_field='filename'):
    """
    Сохранение принятого в form_field файла в указанной директории
    :param upload_dir: Папка, в которой следует сохранить файл
    :param form_field: Имя поля формы, в котором хранится информация о загруженном файле (по-умолчанию - 'filename')
    :return: Строка с ошибкой либо Tuple вида ('Load success', filename)
    """
    form = cgi.FieldStorage()
    if form_field not in form:
        return 'No form field'
    file_item = form[form_field]
    if not file_item.file:
        return 'No file provided'
    if not os.access('tmp', os.F_OK):
        os.makedirs('tmp')
    out_path = os.path.join(upload_dir, file_item.filename)
    with open(out_path, 'wb') as file_out:
        shutil.copyfileobj(file_item.file, file_out, 100000)
    return 'Load succeed', file_item.filename


def _get_html_file_response():
    """
    Чтение HTML-файла с шаблоном страницы ответа на обработку файла.
    :return: Строка шаблона страницы ответа на обработку файла
    """
    f = open('..\\web\\file_result.html')
    return f.read()


def _process_file(file_name):
    """
    Обработка полученного файла и выбача текста сообщения с результатом обработки.
    :param file_name: Имя файла для обработки
    :return: Сообщение с информацией об операции для вывода пользователю
    """
    # Открытие файла
    csv = open('tmp\\' + file_name, 'r')
    text = csv.read()
    # Инициализация списков ошибок и конфликтов
    err_elem = []
    confl_elem = []
    # Выбор типа содержимого (запятая или перенос строки)
    if ',' in text:
        text = text.replace('\n', '').split(',')
    else:
        text = text.split('\n')

    successful = 0
    # Для каждого элемента (логина) из файла
    for el in text:
        # Проверка на корректность
        if not re.fullmatch(r'[0-9A-Za-z.@]+', str(el)):
            err_elem.append(str(el))
            continue
        login = str(el)
        # При наличии домена - его проверка и отсечение
        if '@' in login:
            spl = login.split('@')
            if len(spl) != 2 or '@' + spl[1] != def_mail_domain():
                err_elem.append(el)
                continue
            login = str(spl[0])
        # Попытка записи в базу данных
        resp = requests.post('http://127.0.0.1:8000/db/users/', data={'email': login}, auth=get_auth_data())
        # В случае ошибки - запись в список конфликтов (вероятно, уже существующий пользователь)
        if resp.status_code != 201:
            confl_elem.append(el)
        else:
            successful += 1

    res = '\\n' + 'Users added: ' + str(successful)
    # Печать текста об ошибках и конфликтах
    if len(err_elem) != 0:
        res += '\\n\\n' + 'There are some incorrect elements:'
        for el in err_elem:
            res += '\\n' + str(el)
    if len(confl_elem) != 0:
        res += '\\n\\n' + 'There are some conflict elements:'
        for el in confl_elem:
            res += '\\n' + str(el)
    return res


def _get_response():
    """
    Построение ответа сервера на запрос.
    :return: Ответ сервера на запрос (сообщение с результатом обработки файла)
    """
    res = save_uploaded_file('tmp')
    message = str(res)
    # Если файл сохранён без ошибок
    if res[1]:
        message = res[0] + ': ' + res[1]
        # Обработка данных в файле и приписка результатов к сообщению
        message += _process_file(res[1])
        # Удаление файла
        os.remove('tmp\\' + res[1])
        # Удаление папки
        if os.access('tmp', os.F_OK):
            os.rmdir('tmp')
    html = _get_html_file_response()
    return html.replace('{message}', message)

if __name__ == '__main__':
    print('Content-type:text/html\r\n\r\n')
    print(_get_response())
