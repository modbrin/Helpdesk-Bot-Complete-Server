from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import string
import random
import requests
import smtplib
import sys
import json
import datetime

sys.path.append('..\\py_scripts')
from db_defaults import get_auth_data, def_mail_domain

sys.path.append('..\\bot')
from email_params import get_config

# длина ключа активации
KEY_LENGTH = 5
# количество попыток активации
TRY_LIMIT = 5
# данные почты для отправки писем
EMAIL, EMAIL_PASS, SMTP_SERVER, SMTP_PORT = get_config('outgoing_email.txt')


# сгенерировать ключ из чисел заданной длины в виде строки
def generate_key():
    return ''.join(random.choices(string.digits, k=KEY_LENGTH))


def _send_email(to_address, subject, body):
    """
    Отправляет письмо подтверждения пользователю.
    :param to_address: Адрес получателя
    :param subject: Тема письма
    :param body: Тело письма
    :return: None
    """
    # Присваваем значение почты, с которой отправится письмо
    from_address = EMAIL
    # Собираем объект письма
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    # Открываем соединение через smtp сервер google
    server = smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT))
    server.starttls()
    # Проводим авторизацию
    server.login(from_address, EMAIL_PASS)
    # Преобразуем объект письма в строку
    text = msg.as_string()
    # Отправляем письмо
    server.sendmail(from_address, to_address, text)
    # Закрываем соединение
    server.quit()


def _write_confirmation_to_db(email, confirmation):
    """
    Отправка данных о новом пользователе в базу данных.
    :param email: Почтовый адрес пользователя в назначенном домене
    :param confirmation: Ключ подтверждения, требуемый для верификации аккаунта
    :return: True - успешная операция, False - неудача
    """
    resp = requests.get('http://127.0.0.1:8000/db/users/' + email + '/').json()
    if not resp.get('id'):
        resp_create = requests.post('http://127.0.0.1:8000/db/users/',
                                    data={'email': email, 'activationKey': confirmation},
                                    auth=get_auth_data())
        return resp_create.status_code == 201
    db_id = resp['id']
    resp = requests.put('http://127.0.0.1:8000/db/users/' + str(db_id) + '/',
                        data={'email': email, 'activationKey': confirmation},
                        auth=get_auth_data())
    return resp.status_code == 200


# Отпарвить письмо с ключем на почту
def send_validation(email, user_id):
    # генерируем ключ
    keycode = generate_key()
    user_id = str(user_id)
    if "@" in email:
        email = email[0:email.index("@")]
    # записывем данные в базу и отсылаем письмо
    activation_data = json.dumps(dict(user_id=user_id, key=keycode, limit=1))
    if _write_confirmation_to_db(email, activation_data):
        email += def_mail_domain()
        _send_email(email, "Helpdesk Bot Confirmation",
                    "Your confirmation code is: %s\n\nYou can now enter it in bot." % keycode)
        return True
    return False


# подтвердить ключ
def confirm_keycode(user_id, chat_id, key):
    # получаем список пользователей
    resp = requests.get('http://127.0.0.1:8000/db/users/').json()
    # составляем ключ активации
    # keycode = str(user_id)+str(key)
    # ищем ключ в списке пользователей
    user_id = str(user_id)
    key = str(key)
    for user in resp:
        try:
            activation_data = json.loads(user['activationKey'])
        except Exception:
            continue
        if activation_data['user_id'] == user_id:
            # ищем пользователя с указанным user_id
            if activation_data['key'] == key:
                def_dict = dict(email=user['email'], activationKey='None', userID=user_id, chatID=chat_id)
                # Если ключ правильный, обновляем данные пользователя и удаляем подтверждение из базы
                resp_save = requests.put('http://127.0.0.1:8000/db/users/%s/' % user['id'], data=def_dict,
                                         auth=get_auth_data())
                add_activation_date(user_id)
                return True
            else:
                if activation_data['limit'] >= TRY_LIMIT:
                    # по достижении лимита попыток удаляем код подтверждения
                    def_dict = dict(email=user['email'], activationKey='None')
                    resp_save = requests.put('http://127.0.0.1:8000/db/users/%s/' % user['id'], data=def_dict,
                                             auth=get_auth_data())
                    return 'limit'
                else:
                    # инкрементируем счетчик при неправильном коде
                    activation_data['limit'] += 1
                    def_dict = dict(email=user['email'], activationKey=json.dumps(activation_data))
                    resp_save = requests.put('http://127.0.0.1:8000/db/users/%s/' % user['id'], data=def_dict,
                                             auth=get_auth_data())
                return False
    return False


def add_zero(number):
    if number < 10:
        return "0" + str(number)
    else:
        return str(number)

# добавить пользователю дату активации
def add_activation_date(user_id):
    resp_get = requests.get("http://127.0.0.1:8000/db/users/")
    for user in resp_get.json():
        if user['userID'] == user_id:
            now = datetime.datetime.now()
            # формируем строку с датой
            date = "%s/%s/%s %s:%s" % (now.day, now.month, now.year, add_zero(now.hour), add_zero(now.minute))
            # получаем старые записи о дате
            old_date = []
            try:
                old_date = json.loads(user['activationDate'])
            except json.decoder.JSONDecodeError:
                old_date = []
            if not old_date or str(type(old_date)) == "<class 'str'>":
                old_date = []
            # добавляем текущую дату
            old_date.append(date)
            def_dict = dict(email=user['email'], activationDate=json.dumps(old_date))
            resp_save = requests.put('http://127.0.0.1:8000/db/users/%s/' % user['id'], data=def_dict,
                                     auth=get_auth_data())

# Exempli gratia:
# send_validation('m.surkov','new_user_id')
# confirm_keycode('257347117','chat',51892)
