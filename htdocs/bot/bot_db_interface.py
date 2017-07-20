import requests
import re
# Импортируем библиотеку по абсолютному пути
import importlib.util
import datetime
import json
spec = importlib.util.spec_from_file_location("db_defaults", "C:/Apache24/htdocs/py_scripts/db_defaults.py")
db_defaults = importlib.util.module_from_spec(spec)
spec.loader.exec_module(db_defaults)

# компилируем регулярное выражение для проверки email
EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

# константа хоста сервера
SERVER_URL = "http://10.90.137.54/public/view.py?id="


# Получить email по user_id
def get_email(user_id):
    # Получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/').json()
    # Осуществляем поиск по полученным данным
    for user in resp:
        if user['userID'] == str(user_id):
            return user['email'].strip() + "@innopolis.ru"
    # Если такого user_id нет, возвращаем None
    return None


# Получить user_id по email (email без @innopolis.ru !)
def get_uid(email):
    # Получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/').json()
    # Осуществляем поиск по полученным данным
    for user in resp:
        if user['email'].strip() == str(email).strip():
            return user['userID'].strip()
    # Если такого email нет, возвращаем None
    return None


# Проверка почты регулярным выражением
def is_email(email):
    return bool(EMAIL_REGEX.match(email))


# Проверка является ли почта "*@innopolis.ru"
def is_inno_email(email):
    return is_email(email) and "@innopolis.ru" in email


# Полуение username из email (например abc@mail.ru --> abc)
def cut_domain(email):
    return email[0:email.index('@')] if ('@' in str(email)) else email


# Проверка на существование user_id в базе
def uid_exists(user_id):
    # Получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/').json()
    # Осуществляем поиск по полученным данным
    for user in resp:
        if user['userID'] == str(user_id):
            return True
    # Если такого user_id нет, возвращаем None
    return False


# Проверка на существование email в базе
def email_exists(email):
    # Получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/').json()
    # Осуществляем поиск по полученным данным
    for user in resp:
        if user['email'].strip() == str(email).strip():
            return True
    # Если такого email нет, возвращаем None
    return False


# Назначить пользователю chat_id
def set_chat_id(user_id, chat_id):
    # Получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/').json()
    # Получаем данные авторизации
    auth_data = db_defaults.get_auth_data()
    # Осуществляем поиск по полученным данным
    for user in resp:
        if user['userID'] == str(user_id):
            # Составляем пакет данных, email-обязательное поле
            def_dict = dict(chatID=chat_id, email=user['email'])
            # Отправляем запрос БД
            resp_put = requests.put('http://127.0.0.1:8000/db/users/%s/' % user['id'], data=def_dict, auth=auth_data)
            # Если данные записаны успешно возвращаем True
            return resp_put.status_code == 200
    return False


# Получить chat_id
def get_chat_id(user_id):
    # Получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/').json()
    # Осуществляем поиск по полученным данным
    for user in resp:
        if user['userID'] == str(user_id):
            # Возвращаем chat_id
            return user['chatID'].strip()
    # Если такого user_id нет, возвращаем None
    return None


# Устанавливаем state для пользователя, state-integer!
def set_state(user_id, new_state):
    # Получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/').json()
    # Получаем данные авторизации
    auth_data = db_defaults.get_auth_data()
    # Осуществляем поиск по полученным данным
    for user in resp:
        if user['userID'] == str(user_id):
            # Составляем пакет данных, email-обязательное поле
            def_dict = dict(state=new_state, email=user['email'])
            # Отправляем запрос БД
            resp_put = requests.put('http://127.0.0.1:8000/db/users/%s/' % user['id'], data=def_dict, auth=auth_data)
            # Если данные записаны успешно возвращаем True
            return resp_put.status_code == 200
    return False


# Назначить пользователю состояние
def get_state(user_id):
    # Получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/').json()
    # Осуществляем поиск по полученным данным
    for user in resp:
        if user['userID'] == str(user_id):
            # Возвращаем state
            return user['state']
    # Если такого user_id нет, возвращаем None
    return None


# Назначить пользователю язык
def set_lang(user_id, lang):
    # Получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/').json()
    # Получаем данные авторизации
    auth_data = db_defaults.get_auth_data()
    # Осуществляем поиск по полученным данным
    for user in resp:
        if user['userID'] == str(user_id):
            # Составляем пакет данных, email-обязательное поле
            def_dict = dict(preferredLanguage=lang, email=user['email'])
            # Отправляем запрос БД
            resp_put = requests.put('http://127.0.0.1:8000/db/users/%s/' % user['id'], data=def_dict, auth=auth_data)
            # Если данные записаны успешно возвращаем True
            return resp_put.status_code == 200
    return False


# назначить пользователю язык RU
def set_lang_ru(user_id):
    return set_lang(user_id, "RU")


# Назначить пользователю язык EN
def set_lang_en(user_id):
    return set_lang(user_id, "EN")


# Получить выбранный полбзователем язык, возвращаемые значения (EN, RU)
def get_lang(user_id):
    # Получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/').json()
    # Осуществляем поиск по полученным данным
    for user in resp:
        if user['userID'] == str(user_id):
            # Возвращаем state
            return user['preferredLanguage']
    # Если такого user_id нет, возвращаем None
    return None


# Получить контактную информацию
def get_contact_info():
    # Отправляем запрос не сервер
    resp = requests.get('http://127.0.0.1:8000/db/contact_info/')
    # Если ответ получен успешно, возвращаем текст контактной информации
    return resp.json()[0]["info"] if resp.status_code == 200 else None


# Добавление нового отзыва в БД (grade - integer)
def newFeedback(name, email, grade, text):
    # Получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/feedback/').json()
    # Получаем данные авторизации
    auth_data = db_defaults.get_auth_data()
    # Получаем текущее время, для подписи отзывов
    now = datetime.datetime.now()
    # Осуществляем поиск по полученным данным
    for entry in resp:
        if entry['email'] == email:
            # Составляем пакет данных, меняем рейтинг и добавляем новый комментарий
            old_text = entry['text']
            # Если получен новый текст комментария, то добавляем его к старому с отступом и временем добавления
            if text.strip():
                old_text += now.strftime("%Y-%m-%d %H:%M")+ " (rating: "+ grade + "/5)  " + text  + '<br>'
            def_dict = dict(grade=grade, text=old_text)
            # Отправляем запрос БД
            resp_put = requests.put('http://127.0.0.1:8000/db/feedback/%s/' % entry['id'], data=def_dict,
                                    auth=auth_data)
            # Если данные записаны успешно возвращаем True
            return resp_put.status_code == 200
    # Создаем форму отправки для нового комментария, это необходимо если пользователь
    # не найден в существующих комментариях
    def_dict = dict(name=name, email=email, grade=grade, text=now.strftime("%Y-%m-%d %H:%M") + " (rating: "+ grade + "/5)  " + text + '<br>')
    # Отправляем серверу
    resp = requests.post('http://127.0.0.1:8000/db/feedback/', data=def_dict,
                         auth=db_defaults.get_auth_data())
    # Проверяем, успешно ли записалось
    return resp.status_code == 201


# Получить словарь статей {title:url, ...}, макс. количество элементов - 2
def get_article_list(token_list):
    # Удаляем пустые элементы из массива
    token_list = list(filter(None, token_list))
    #
    if not token_list:
        return {}
    # отправляем запрос серверу
    resp = requests.get('http://127.0.0.1:8000/db/' + get_token_string(token_list))
    result = {}
    # составляем словарь статей
    for article in resp.json():
        result[article["title"]] = make_server_link(article["id"])
    return result


# Преобразовать массив токенов в строку поиска http
def get_token_string(token_list):
    result = "YXvTpGxdL3ZRMRd0nVDuRMR"
    # преобразуем массив слов в строку поиска http
    for token in token_list:
        result += '&' + token
    # возврвщаем строку
    return result


# Получить полную ссылку по id статьи для пользователя
def make_server_link(id):
    return SERVER_URL + str(id)

# получить id тикета по user_id
def get_ticket_id(user_id):
    # получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/')
    # проверяем успешность запроса
    if resp.status_code != 200:
        return 0
    # преобразуем данные в json
    resp = resp.json()
    # ищем пользователя и возвращаем id текущего тикета
    for user in resp:
        if user['userID'] == str(user_id):
            return user['ticketID']


# назначить ticket_id по user_id
def set_ticket_id(user_id, ticket_id):
    # Получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/').json()
    # Получаем данные авторизации
    auth_data = db_defaults.get_auth_data()
    # Осуществляем поиск по полученным данным
    for user in resp:
        if user['userID'] == str(user_id):
            # Составляем пакет данных, email-обязательное поле
            def_dict = dict(ticketID=ticket_id, email=user['email'])
            # Отправляем запрос БД
            resp_put = requests.put('http://127.0.0.1:8000/db/users/%s/' % user['id'], data=def_dict, auth=auth_data)
            # Если данные записаны успешно возвращаем True
            return resp_put.status_code == 200
    return False


# получить rating по user_id
def get_rating(user_id):
    # получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/')
    # проверяем успешность запроса
    if resp.status_code != 200:
        return 0
    # преобразуем данные в json
    resp = resp.json()
    # ищем пользователя и возвращаем rating
    for user in resp:
        if user['userID'] == str(user_id):
            return user['rating']


# назначить rating по user_id
def set_rating(user_id, rating):
    # Получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/').json()
    # Получаем данные авторизации
    auth_data = db_defaults.get_auth_data()
    # Осуществляем поиск по полученным данным
    for user in resp:
        if user['userID'] == str(user_id):
            # Составляем пакет данных, email-обязательное поле
            def_dict = dict(rating=rating, email=user['email'])
            # Отправляем запрос БД
            resp_put = requests.put('http://127.0.0.1:8000/db/users/%s/' % user['id'], data=def_dict, auth=auth_data)
            # Если данные записаны успешно возвращаем True
            return resp_put.status_code == 200
    return False


# Получить сообщение вопроса
def get_message_content(user_id):
    # получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/')
    # проверяем успешность запроса
    if resp.status_code != 200:
        return 0
    # преобразуем данные в json
    resp = resp.json()
    # ищем пользователя и возвращаем rating
    for user in resp:
        if user['userID'] == str(user_id):
            return user['messageContent']


# Добавить текст к вопросу
def add_message_content(user_id, text):
    # получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/').json()
    # Получаем данные авторизации
    auth_data = db_defaults.get_auth_data()
    # Осуществляем поиск по полученным данным
    for user in resp:
        if user['userID'] == str(user_id):
            # Составляем пакет данных, email-обязательное поле
            new_content = user['messageContent'].strip() if user['messageContent'] != "null" else ""
            new_content += " " + text.strip()
            def_dict = dict(messageContent=new_content, email=user['email'])
            # Отправляем запрос БД
            resp_put = requests.put('http://127.0.0.1:8000/db/users/%s/' % user['id'], data=def_dict, auth=auth_data)
            # Если данные записаны успешно возвращаем True
            return resp_put.status_code == 200
    return False


# Удалить поле вопроса
def clear_message_content(user_id):
    # получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/')
    # Получаем данные авторизации
    auth_data = db_defaults.get_auth_data()
    # преобразуем данные в json
    resp = resp.json()
    # ищем пользователя и удаляем message_content
    for user in resp:
        if user['userID'] == str(user_id):
            # Составляем пакет данных, email-обязательное поле
            def_dict = dict(messageContent="null", email=user['email'])
            # Отправляем запрос БД
            resp_put = requests.put('http://127.0.0.1:8000/db/users/%s/' % user['id'], data=def_dict, auth=auth_data)
            # Если данные записаны успешно возвращаем True
            return resp_put.status_code == 200
    return False

# получть список вложений
def get_message_att(user_id):
    # получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/')
    # проверяем успешность запроса
    if resp.status_code != 200:
        return 0
    # преобразуем данные в json
    resp = resp.json()
    # ищем пользователя и возвращаем rating
    for user in resp:
        if user['userID'] == str(user_id):
            if not user['messageAtt']:
                return []
            return json.loads(user['messageAtt'])

# добавить элемент в список вложений
def add_message_att(user_id, attachment):
    # получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/').json()
    # Получаем данные авторизации
    auth_data = db_defaults.get_auth_data()
    # Осуществляем поиск по полученным данным
    for user in resp:
        if user['userID'] == str(user_id):
            # Составляем пакет данных, email-обязательное поле
            old_list = json.loads(user['messageAtt']) if user['messageAtt'] else []
            old_list.append(str(attachment))
            def_dict = dict(messageAtt=json.dumps(old_list), email=user['email'])
            # Отправляем запрос БД
            resp_put = requests.put('http://127.0.0.1:8000/db/users/%s/' % user['id'], data=def_dict, auth=auth_data)
            # Если данные записаны успешно возвращаем True
            return resp_put.status_code == 200
    return False

# очистить список вложений
def clear_message_att(user_id):
    # получаем данные о пользователях
    resp = requests.get('http://127.0.0.1:8000/db/users/').json()
    # Получаем данные авторизации
    auth_data = db_defaults.get_auth_data()
    # Осуществляем поиск по полученным данным
    for user in resp:
        if user['userID'] == str(user_id):
            # Составляем пакет данных, email-обязательное поле
            def_dict = dict(messageAtt="[]", email=user['email'])
            # Отправляем запрос БД
            resp_put = requests.put('http://127.0.0.1:8000/db/users/%s/' % user['id'], data=def_dict, auth=auth_data)
            # Если данные записаны успешно возвращаем True
            return resp_put.status_code == 200
    return False
