#!python.exe
import cgi
import sys
import requests
from send_message import send_hello_message

# import email_validator
# import db_defaults
# import hello_message
sys.path.append('..\\py_scripts')
from email_validator import construct_confirmation, decrypt_uid
from db_defaults import get_auth_data
sys.path.append('..\\public')

# http://our_site.innopolis.ru/public/confirm.py?id=123&chat=123&email=i.ivanov&key=securekey

print('Content-type:text/html\r\n\r\n')

def _get_printable_info():
        """
        Построение ответа сервера на запрос.
        :return: Ответ сервера на запрос
        """
        form = cgi.FieldStorage()
        user_id = form.getvalue('id')
        if not user_id:
            return 'User ID is required'
        user_id = decrypt_uid(user_id)
        chat_id = form.getvalue('chat')
        if not chat_id:
            return 'Chat ID is required'
        chat_id = decrypt_uid(chat_id)
        # import smth
        email = form.getvalue('email')
        if not email:
            return 'Email is required'
        key = form.getvalue('key')
        if not key:
            return 'Key is required'

        resp = requests.get('http://127.0.0.1:8000/db/users/' + email + '/')
        if resp.status_code != 200:
            return 'User not found'

        our_user = resp.json()
        # Сверка ключа из ссылки с хэш-ключом в базе данных
        if our_user['activationKey'] == 'None' or our_user['activationKey'] != construct_confirmation(user_id, email, key):
            return 'Key is incorrect'

        resp = requests.put('http://127.0.0.1:8000/db/users/' + str(our_user['id']) + '/',
                            data={'email': email, 'userID': user_id, 'chatID': chat_id, 'activationKey': 'None'}, auth=get_auth_data())
        if resp.status_code != 200:
            return 'DB authentication failed! Please, try again later.'
        print('User was successfully added! Check your chat with bot to start conversation.')
        send_hello_message(int(user_id), int(chat_id))


# Построение ответа
print(_get_printable_info())
