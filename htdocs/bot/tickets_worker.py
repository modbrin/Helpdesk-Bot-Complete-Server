from email_params import get_config
from requests import session
import os

payload = {
    'action': 'login',
    'pro_user[email]': None,  # <-- Почта для логина
    'pro_user[password]': None  # <-- Пароль для логина
}
sw_host = "http://127.0.0.1:9093"  # <-- адрес с портом на котором установлен Spiceworks

def getPayload(filename):
    f = open(filename, 'r')
    #считывает логин, пароль и адрес sw
    index = 0
    for line in f:
        if(index == 0):
            payload['pro_user[email]'] = line[0:len(line)-1]
        if(index == 1):
            payload['pro_user[password]'] = line[0:len(line)-1]
        if(index == 2):
            sw_host = line[0:len(line)-1]
        index += 1
    return



# ищем все тикеты с данным summary
def searchForTickets(whole_json, creator):
    result = []
    # итерируемся по всем тикетам и сравниваем summary
    for ticket in whole_json:
        # если summary найден то добавляем в список
        if ticket["creator"]["email"] == creator:
            result.append(ticket)
    return result


def searchTicketById(whole_json, id):
    for ticket in whole_json:
        if ticket["id"] == id:
            print()
            return ticket
    return {}


# Получить содержание тикета - вопрос пользователя
def getTicketContent(ticket_json):
    return ticket_json["description"]


# Получить фрагмент тикета - все комментарии
def listComments_json(ticket_json):
    return ticket_json["public_comments"]


# Получить комментарии в виде массива строк(их содержания), упорядоченные по времени
def listComments(ticket_json):
    result = []
    for comment in reversed(listComments_json(ticket_json)):
        result.append(comment["body"])
    return result



# Получить все тикеты в формате json где ключи-вопросы, значения-массивы комментариев
def __getTickets__(tickets_json):
    result = {}
    for ticket in tickets_json:
        content = getTicketContent(ticket)
        if "<br />" in content:
            content = content[0:content.index("<br />")]
        result[ticket["id"]] = content
    return result


# в этом случае я предлагаю хранить почту пользователя в Summary и искать по ней
def getOpenedTickets(email_search):
    with session() as c:
        # Получаем информацию из sw_acc.txt для подключения
        getPayload('sw_acc.txt')
        # Проводим авторизацию  в Spiceworks
        c.post(sw_host + '/pro_users/login', data=payload)
        # Получаем все открытые тикеты пользователя
        response = c.get(sw_host + '/api/tickets.json?total_count:true&filter=open')
        if response.status_code != 200:
            return None
        result = response.json()
        # Обрабатываем полученные результаты и укладываем необходимые нам данные в json
        tickets = searchForTickets(result, email_search)
        return __getTickets__(tickets)


def getClosedTickets(email_search):
    with session() as c:
        # Получаем информацию из sw_acc.txt для подключения
        getPayload('sw_acc.txt')
        # Проводим авторизацию  в Spiceworks
        c.post(sw_host + '/pro_users/login', data=payload)
        # Получаем все закрытые тикеты пользователя
        response = c.get(sw_host + '/api/tickets.json?total_count:true&filter=closed')
        if response.status_code != 200:
            return None
        result = response.json()
        # Обрабатываем полученные результаты и укладываем необходимые нам данные в json
        tickets = searchForTickets(result, email_search)
        return __getTickets__(tickets)


def getAllTickets(email_search):
    with session() as c:
        # Получаем информацию из sw_acc.txt для подключения
        getPayload('sw_acc.txt')
        # Проводим авторизацию  в Spiceworks
        c.post(sw_host + '/pro_users/login', data=payload)
        # Получаем все тикеты пользователя
        response = c.get(sw_host + '/api/tickets.json?total_count:true')
        if response.status_code != 200:
            return None
        result = response.json()
        # Обрабатываем полученные результаты и укладываем необходимые нам данные в json
        tickets = searchForTickets(result, email_search)
        return __getTickets__(tickets)


# Получить тикет по id. Представлен в формате {title:[comment,comment,etc...]}
def getTicketById(id_search):
    with session() as c:
        # Получаем информацию из sw_acc.txt для подключения
        getPayload('sw_acc.txt')
        id_search = int(id_search)
        # Проводим авторизацию  в Spiceworks
        c.post(sw_host + '/pro_users/login', data=payload)
        # Получаем все тикеты пользователя
        response = c.get(sw_host + '/api/tickets.json?total_count:true')
        if response.status_code != 200:
            return None
        result = response.json()
        # Обрабатываем полученные результаты и укладываем необходимые нам данные в json
        ticket = searchTicketById(result, id_search)
        content = getTicketContent(ticket)
        if "<br />" in content:
            content = content[0:content.index("<br />")]
        return {content:listComments(ticket)}

photo_extensions = ['jpg','png','jpeg']

def is_photo_attachment(path):
    if '.' not in path:
        return False
    extension = path[path.rindex('.')+1:]
    extension = extension.lower().strip()
    return extension in photo_extensions

#Получить по id лист, содержащий все вложения от пользователя к тикету
def get_user_att(id_search):
    with session() as c:
        # Получаем информацию из sw_acc.txt для подключения
        getPayload('sw_acc.txt')
        id_search = int(id_search)
        # Проводим авторизацию  в Spiceworks
        c.post(sw_host + '/pro_users/login', data=payload)
        # Получаем все тикеты пользователя
        response = c.get(sw_host + '/api/tickets.json?total_count:true')
        if response.status_code != 200:
            return None
        result = response.json()
        # Обрабатываем полученные результаты и укладываем необходимые нам данные в json
        ticket = searchTicketById(result, id_search)
        comments = listComments_json(ticket)
        result = []
        result_photos = []
        bot_email = get_config('outgoing_email.txt')[0]
        bot_email = bot_email[0:len(bot_email)-1]
        for com in comments:
            if (com["attachment_name"]!= None and com['creator']['email'] == bot_email):
                path = com["attachment_location"]
                path = os.path.basename(path).strip()
                path = path[path.index('-')+1:]
                result.append(path[:path.rindex('.')]) if not is_photo_attachment(path) else result_photos.append(path[:path.rindex('.')])
        result = list(set(result))
        result_photos = list(set(result_photos))
        return result, result_photos

#Получить по id лист, содержащий все вложения от администратора к тикету
def get_sw_att(id_search):
    with session() as c:
        # Получаем информацию из sw_acc.txt для подключения
        getPayload('sw_acc.txt')
        id_search = int(id_search)
        # Проводим авторизацию  в Spiceworks
        c.post(sw_host + '/pro_users/login', data=payload)
        # Получаем все тикеты пользователя
        response = c.get(sw_host + '/api/tickets.json?total_count:true')
        if response.status_code != 200:
            return None
        result = response.json()
        # Обрабатываем полученные результаты и укладываем необходимые нам данные в json
        ticket = searchTicketById(result, id_search)
        comments = listComments_json(ticket)
        result = []
        result_photos = []
        bot_email = get_config('outgoing_email.txt')[0]
        bot_email = bot_email[0:len(bot_email)-1]
        for com in comments:
            if (com["attachment_name"]!= None and com['creator']['email'] != bot_email):
                path = com["attachment_location"]
                result.append(path) if not is_photo_attachment(path) else result_photos.append(path)
        result = list(set(result))
        result_photos = list(set(result_photos))
        return result, result_photos
# Пример
#отправить пользователю все доступные тикеты (открытые/закрытые/все)
#print(getOpenedTickets('a.samatov@innopolis.ru'))
#получить id нужного тикета
#id = input('введите id тикета\n')
#получаем dict вида description:comments[] из sw
#ticket = getTicketById(id)
#делаем строку из содержимого
#key = list(ticket.keys())[0]
#msg = key
#for comment in ticket[key]:
    #msg+="\n"+comment
#отправляем ее пользователю
#print(msg)
#отправляем пользователю вложения, если есть
#attList1 = get_sw_att(175)
#print('sw att:')
#for att_path in attList1:
    #print(att_path)
#attList2 = get_user_att(175)
#print('user att:')
#for att_path in attList2:
    #print(att_path)
    #отправить пользователю вложение
