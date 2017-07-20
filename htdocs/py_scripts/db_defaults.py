def get_auth_data():
    """
    :return: Tuple из значений (login, password) для доступа к базе данных
    """
    return 'admin', 'qwerty123'


def def_title():
    """
    :return: Заголовок статьи по-умолчанию
    """
    return 'New article'


def def_text():
    """
    :return: Текст статьи по-умолчанию
    """
    return '<p><br></p>'


def def_keywords():
    """
    :return: Ключевые слова статьи по-умолчанию
    """
    return 'keyword'


def def_user():
    """
    :return: Почта нового пользователя по-умолчанию
    """
    return 'default_user'


def def_mail_domain():
    """
    :return: Домен всех почтовых адресов по-умолчанию
    """
    return '@innopolis.ru'


def button_en():
    """
    :return: Текст кнопки полезности статьи (английский вариант)
    """
    return 'Problem solved'


def button_ru():
    """
    :return: Текст кнопки полезности статьи (русский вариант)
    """
    return 'Проблема решена'


def def_host():
    """
    :return: Начало адреса сайта
    """
    return 'http://10.90.137.54'


def email_header():
    """
    :return: Тема письма подтверждения электронной почты
    """
    return 'NoReply: HelpDesk Bot'


def email_message():
    """
    :return: Текст письма подтверждения электронной почты
    """
    return 'You received this email because someone claimed it to confirm unidentified telegram account,' + \
           'if that was not you, ignore the message.'


def cypher_key():
    """
    :return: Ключ шифровки и расшифровки user_id
    """
    return b'yP7j9ZwVU8csIhUWY_AlUoYYjOjps8LqTKa11nAiZlw='
