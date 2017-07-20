import sys
import requests
from random import choice
from string import ascii_letters, digits

sys.path.append('..\\py_scripts')
from email_validator import _send_email
from db_defaults import get_auth_data
sys.path.append('..\\bot')


# Добавление нового пользователя по email, позволяет назначить ему userID и chatID
def tryPutUserWithEmail(newUID, chatID, invite):
    # Запрашиваем из базы пользователя
    invite_search = requests.get("http://127.0.0.1:8000/db/invites/")
    email = None
    invite_id = None
    # пытаемся получить email и id записи по коду инвайта
    for entry in invite_search.json():
        if entry['invite'] == invite:
            email = entry['email']
            invite_id = entry['id']
            break
    # если email так и не найден возвращаем неуспех
    if not email:
        return False
    resp = requests.get('http://127.0.0.1:8000/db/users/%s/' % email)
    # Если пользователь не найден завершаем создаем пользователя
    if resp.status_code != 200:
        def_dict = dict(email=email, userID=newUID, chatID=chatID, activationKey='None')

        # Попытка создания пользователя в базе данных
        resp_user = requests.post('http://127.0.0.1:8000/db/users/', data=def_dict, auth=get_auth_data())

        # Если создание пользователя в базе данных не удалось возвращаем неуспех
        if resp_user.status_code != 201:
            return False
        else:
            # если инвайт использован успешно, удаляем его
            resp = requests.delete('http://127.0.0.1:8000/db/invites/%s/' % invite_id, auth=get_auth_data())
            return True
    else:
        # Получаем данные пользователя
        our_user = resp.json()
        # Если у пользователя уже есть userID возвращаем неуспех
        if our_user['userID']:
            return False
        else:
            # Если данные совпадают, назначаем пользователю новыe userID и chatID, сбрасываем ключ активации
            auth_data = get_auth_data()
            resp = requests.put('http://127.0.0.1:8000/db/users/' + str(our_user['id']) + '/',
                                data={'email': email, 'userID': newUID, 'activationKey': 'None', 'chatID': chatID},
                                auth=auth_data)
            # После удачного запроса к БД возвращаем успех, если произошла ошибка возвращаем неуспех
            if resp.status_code != 200:
                return False
            else:
                # если инвайт использован успешно, удаляем его
                requests.delete('http://127.0.0.1:8000/db/invites/%s/' % invite_id, auth=get_auth_data())
                return True
