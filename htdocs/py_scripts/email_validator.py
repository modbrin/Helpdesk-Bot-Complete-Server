"""
Для бота:
try_confirm(user_id, 'i.ivanov', chat_id)

Для веб-сервера:
decrypt_uid(encoded_uid)
construct_confirmation(user_id, email, key) - user_id должен быть уже расшифрованный

Пример ссылки:
http://our_site.innopolis.ru/public/confirm.py?id=123&chat=123&email=i.ivanov&key=securekey
"""
from random import choice
from string import ascii_letters, digits
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from cryptography.fernet import Fernet
import hashlib
import requests
import smtplib

from db_defaults import get_auth_data, def_mail_domain, def_host, email_header, email_message, cypher_key

# Константы для почты
HOST = def_host()
HEADER = email_header()
MESSAGE = email_message()
KEY = cypher_key()


# Константы
INV_HEADER = "IT HelpDesk Bot Invite"

INV_MESSAGE_RU = "Привет, представляем нового бота технической поддержки ИТ отдела Университета Иннополис!\n" + \
                 "В случае возникновения проблем с техникой в университете ты можешь задать вопрос боту."

INV_MESSAGE_EN = "Hello, we would like to invite you in Innopolis University IT HelpDesk Telegram bot!\n" + \
                 "In case of any technical issue you can ask bot for help.\n\n"

BOT_HOST = "http://telegram.me/InnoITDepartmentBot?start="


def _send_email(to_address, subject, body):
    """
    Отправляет письмо подтверждения пользователю.
    :param to_address: Адрес получателя
    :param subject: Тема письма
    :param body: Тело письма
    :return: None
    """
    # Присваваем значение почты, с которой отправится письмо
    from_address = 'simpletestfortgbot@gmail.com'
    # Собираем объект письма
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    # Открываем соединение через smtp сервер google
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    # Проводим авторизацию
    server.login(from_address, 'hellodarknessmyoldfriend')
    # Преобразуем объект письма в строку
    text = msg.as_string()
    # Отправляем письмо
    server.sendmail(from_address, to_address, text)
    # Закрываем соединение
    server.quit()


def construct_confirmation(user_id, email, key):
    """
    Создание хэш-ключа из 3-х аргументов пользователя.
    :param user_id: ID пользователя в Telegram
    :param email: Почтовый адрес пользователя в назначенном домене
    :param key: Дополнительный ключ
    :return: Хэш-ключ по 3-м аргументам
    """
    # Убеждаемся, что user_id и email не содержат отступов
    user_id = str(user_id).strip()
    email = str(email).strip()
    # Объединяем их в одну строку и переводим в байты
    result = str(user_id + email + key).encode('utf-8')
    # Хэшируем строку sha256
    return hashlib.sha256(result).hexdigest()


def _generate_key():
    """
    Генерация дополнительного ключа пользователя.
    :return: Случайный ключ длиной 50 из цифр и латинских букв
    """
    return ''.join(choice(ascii_letters + digits) for i in range(50))


def _send_email_with_confirmation(user_id, chat_id, email, key):
    """
    Формирование данных для отправки в письме и последующая отсылка самого письма.
    :param user_id: ID пользователя в Telegram
    :param chat_id: ID чата с пользователем в Telegram
    :param email: Почтовый адрес пользователя в назначенном домене
    :param key: Дополнительный ключ
    :return: None
    """
    # Формирование текста письма и ссылки в нём
    message = MESSAGE + '\n\n' + HOST + '/public/confirm.py?id=%s&chat=%s&email=%s&key=%s' \
                                        % (user_id, chat_id, email, key)
    # Отправка письма
    _send_email(email + def_mail_domain(), HEADER, message)


def _write_data_to_db(email, confirmation):
    """
    Отправка данных о новом пользователе в базу данных.
    :param email: Почтовый адрес пользователя в назначенном домене
    :param confirmation: Ключ подтверждения, требуемый для верификации аккаунта
    :return: True - успешная операция, False - неудача
    """
    resp = requests.get('http://127.0.0.1:8000/db/users/' + email + '/').json()
    if not resp.get('id'):
        return False
    db_id = resp['id']
    resp = requests.put('http://127.0.0.1:8000/db/users/' + str(db_id) + '/',
                        data={'email': email, 'activationKey': confirmation},
                        auth=get_auth_data())
    return resp.status_code == 200


# Генерируем ключ только из символов ascii и цифр
def generateInvite():
    return ''.join(choice(ascii_letters + digits) for i in range(55))


# получить новый инвайт, который уже не присутствует в списке
def getInvite(email):
    # получаем полный список всех инвайтов
    resp = requests.get("http://127.0.0.1:8000/db/invites/")
    # создаем сет для элементов
    existing = set()
    # добавляем существующие коды инвайтов в сет и сразу смотрим - если указанный email уже существует, то возвращаем его инвайт
    for entry in resp.json():
        existing.add(entry['invite'])
        if entry['email'] == email:
            return entry['invite']
    # создаем новый инвайт либо получаем уже существующий
    new_invite = generateInvite()
    # если инвайт уже существует генерируем новый и так пока не найдем новый
    while new_invite in existing:
        new_invite = generateInvite()
    # возвращаем новый уникальный инвайт
    return new_invite


# Отправление приглашения пользователю по email
def sendEmailWithInvite(email):
    # простая проверка email чтобы избежать исключений
    if not email:
        return False
    # получаем инвайт по почте
    invite = getInvite(email)
    # составляем письмо
    link = "Here is your link / Вот твоя пригласительная ссылка:\n" + BOT_HOST + invite
    message = INV_MESSAGE_EN + INV_MESSAGE_RU + "\n\n" + link

    # пытаемся добавить пользователя в таблицу инвайтов c полученным кодом инвайта
    def_dict = dict(invite=invite, email=email, is_valid="1")
    resp = requests.post("http://127.0.0.1:8000/db/invites/", def_dict, auth=get_auth_data())

    # обрабытваем ответ сервера, 201 - все успешно, 400 - пользователь уже существует
    if resp.status_code != 201 and resp.status_code != 400:
        return False
    # отправляем приглашение пользователю
    _send_email(email + "@innopolis.ru", INV_HEADER, message)
    return True


def try_confirm(user_id, email, chat_id):
    """
    Создание ключа, сохранение его в базе данных в поле
    соответствующего пользователя и отправка ему письма подтверждения.
    :param user_id: ID пользователя в Telegram
    :param chat_id: ID чата с пользователем в Telegram
    :param email: Почтовый адрес пользователя в назначенном домене
    :return: True - успешная операция, False - неудача
    """
    if "@" in email:
        email = email[0:email.index("@")]
    # Создаем промежутоный ключ
    key = str(_generate_key())
    # Приводим все переменные к str
    user_id = str(user_id)
    chat_id = str(chat_id)
    email = str(email)
    # Генерируем ключ подверждения
    confirmation = construct_confirmation(user_id, email, key)
    # Записываем в базу ключ подтверждения для пользователя с конкретным email
    if _write_data_to_db(email, confirmation):
        # Перешифруем user_id, чтобы его нельзя было использовать для определения Telegram-аккаунта
        user_id = _encrypt_uid(user_id)
        # То же действие для chat_id
        chat_id = _encrypt_uid(chat_id)
        # Отправляем письмо с ссылкой подтверждения
        _send_email_with_confirmation(user_id, chat_id, email, key)
        # Возвращаем успех
        return True
    else:
        sendEmailWithInvite(email)
        # Если email не найден - возвращаем неуспех
        return True


def _encrypt_uid(user_id):
    """
    Зашифровка ID пользователя.
    :param user_id: ID пользователя в Telegram
    :return: Шифр на основе user_id
    """
    f = Fernet(KEY)
    token = f.encrypt(user_id.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_uid(encoded_uid):
    """
    Расшифровка ID пользователя.
    :param encoded_uid: Зашифрованный user_id
    :return: ID пользователя в Telegram
    """
    f = Fernet(KEY)
    token = f.decrypt(encoded_uid.encode("utf-8"))
    return token.decode("utf-8")




# TESTING
if __name__ == '__main__':
    try_confirm('12345', 'd.chernikov', '12345')
