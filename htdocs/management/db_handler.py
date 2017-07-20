import requests
import time
import os
import datetime
from  tkinter import *
from tkinter import filedialog
import json

sys.path.append('..\\py_scripts')
from db_defaults import get_auth_data
sys.path.append('..\\management')

# Удаление всех пользрвателей
def delete_users():
    # подтверждение
    if not confirm():
        print("Cancelled by user")
        return
    # загружаем список всех пользователей
    users = requests.get("http://127.0.0.1:8000/db/users/")
    # проверяем успешность запроса
    if users.status_code != 200:
        print("Database unreachable")
        return
    # парсим данные в json
    users = users.json()
    # считаем пользователей
    counter = 0
    for user in users:
        counter += 1
    current_counter = 1
    print("Starting...")
    # итерируемся по всем пользователям
    for user in users:
        # удаляем пользователя по id
        resp_delete = requests.delete("http://127.0.0.1:8000/db/users/%s/" % user['id'], auth=get_auth_data())
        # проверяем успешность запроса
        if resp_delete.status_code != 204:
            print("Deletion error")
            return
        # собираем строку с информацией о прогрессе
        line = "\rDeleting: %s of %s" % (current_counter, counter)
        # каждые 5 пользователей выводим информацию в консоль
        if current_counter % 5 == 0:
            print(line, end='', flush=True)
        current_counter += 1
    time.sleep(0.5)
    print("\rFinished, deleted %s users" % counter)

# Получить текущую дату и время
def get_date():
    now = datetime.datetime.now()
    return "%s.%s.%s_%s-%s-%s" % (now.hour, now.minute, now.second, now.day, now.month, now.year)

# сохраняем таблицу пользователей в файл
def make_users_file():
    # получаем список всех пользователей
    users = requests.get("http://127.0.0.1:8000/db/users/")
    # проверяем успешность запроса
    if users.status_code != 200:
        print("Database unreachable")
        return
    # парсим данные в json
    users = users.json()
    # убеждаемся в наличии папки для сохранения
    if not os.path.exists("user_dumps"):
        os.makedirs("user_dumps")
    # генерируем имя файла
    filename = get_date() + "_users.json"
    # создаем файл и записываем в него данные
    outfile = open("%s/user_dumps/%s" % (os.getcwd(), filename), "a")
    json.dump(users, outfile)
    # выводим информационное сообщение
    print("Users saved to /user_dumps/" + filename)

# Декоративная функция
def getProgress(num):
    num = num % 4
    if num == 0:
        return "\\"
    elif num == 1:
        return "/"
    elif num == 2:
        return "―"
    else:
        return "|"

# Загрузить пользователей из файла
def load_users_file():
    # убеждаемся в наличии файла
    if not os.path.exists("user_dumps"):
        os.makedirs("user_dumps")
    # открываем окно загрузки файла
    root = Tk()
    root.filename = filedialog.askopenfilename(initialdir=os.getcwd() + "/user_dumps/", title="Choose your file",
                                               filetypes=(("JSON files", "*.json"), ("all files", "*.*")))
    # закрываем окно загрузки
    root.withdraw()
    # если пользователь не выбрал файла завершаем
    if not root.filename:
        print("Cancelled by user")
        return
    # открываем полученный файл
    infile = open(root.filename, "r")
    # выгружаем данные из файла
    users = json.load(infile)
    # инициализиуем счетчики количества
    counter_ok = 0
    counter_err = 0
    total = 0
    print("Starting...")
    # итерируемся по всем пользователям и добавляем в текущую базу
    for user in users:
        def_dict = dict(userID=user['userID'], chatID=user['chatID'], email=user['email'],
                        preferredLanguage=user['preferredLanguage'], state=user['state'],
                        activationKey=user['activationKey'])
        resp = requests.post("http://127.0.0.1:8000/db/users/", data=def_dict, auth=get_auth_data())
        # считаем количество успехов/неуспехов
        if resp.status_code == 201:
            counter_ok += 1
        else:
            counter_err += 1
        total += 1
        # каждые 5 пользователей выводим строку с информацией
        if total % 5 == 0:
            print(
                "\rAdding users: %s successful, %s unsuccessful%s" % (
                    counter_ok, counter_err, getProgress(total / 5 % 3 + 1)),
                end='', flush=True)
    time.sleep(0.5)
    print("\rFinished adding users: %s successful, %s unsuccessful" % (counter_ok, counter_err), end='', flush=True)

# Удаление всех пользователей
def delete_articles():
    # подтверждение
    if not confirm():
        print("Cancelled by user")
        return
    # получаем список статей
    articles = requests.get("http://127.0.0.1:8000/db/")
    # проверяем успешность запроса
    if articles.status_code != 200:
        print("Database unreachable")
        return
    # парсим данные в json
    articles = articles.json()
    # считаем количество статей
    counter = 0
    for article in articles:
        counter += 1
    current_counter = 1
    print("Starting...")
    # итерируемся по статьям
    for article in articles:
        # удаляем статью по id
        resp_delete = requests.delete("http://127.0.0.1:8000/db/%s/" % article['id'], auth=get_auth_data())
        # проверяем успешность запроса
        if resp_delete.status_code != 204:
            print("Deletion error")
            return
        # формируем строку с информацией о прогрессе
        line = "\rDeleting: %s of %s" % (current_counter, counter)
        # выводим информацию каждые 5 статей
        if current_counter % 5 == 0:
            print(line, end='', flush=True)
        current_counter += 1
    time.sleep(1)
    print("\rFinished, deleted %s articles" % counter)

# сохраняем все статьи в файл
def make_articles_file():
    # получаем список статей
    articles = requests.get("http://127.0.0.1:8000/db/")
    # проверяем успешность запроса
    if articles.status_code != 200:
        print("Database unreachable")
        return
    # парсим данные в json
    articles = articles.json()
    # убеждаемся наличии папки
    if not os.path.exists("article_dumps"):
        os.makedirs("article_dumps")
    # генерируем имя файла
    filename = get_date() + "_articles.json"
    # открываем файл и запичываем в него данные
    outfile = open("%s/article_dumps/%s" % (os.getcwd(), filename), "a")
    json.dump(articles, outfile)
    print("Articles saved to /article_dumps/" + filename)

# Загрузить статьи из файла
def load_articles_file():
    # убеждаемся в наличии папки
    if not os.path.exists("article_dumps"):
        os.makedirs("article_dumps")
    # открываем окно загрузки файла
    root = Tk()
    root.filename = filedialog.askopenfilename(initialdir=os.getcwd() + "/article_dumps/", title="Choose your file",
                                               filetypes=(("JSON files", "*.json"), ("all files", "*.*")))
    # закрываем окно
    root.withdraw()
    # если пользователь не выбрал файла завершаем
    if not root.filename:
        print("Cancelled by user")
        return
    # открываем файл
    infile = open(root.filename, "r")
    # загружаем данные
    articles = json.load(infile)
    # инициализируем счетчики
    counter_ok = 0
    counter_err = 0
    total = 0
    print("Starting...")
    # получаем список статей в базе для того чтобы не добавлять существующие
    current_articles = requests.get("http://127.0.0.1:8000/db/").json()
    # итерируемся по статьям
    for article in articles:
        def_dict = dict(created=article['created'], text=article['text'], keywords=article['keywords'],
                        title=article['title'], viewCount=article['viewCount'],
                        likeCount=article['likeCount'])
        # сверяемся с текущей данной - ищем статью по заголовку, существующие не добавляем
        exists = False
        for element in current_articles:
            if element['title'] == def_dict['title']:
                exists = True
        if exists:
            total += 1
            counter_err += 1
            continue
        # записываем статью в базу
        resp = requests.post("http://127.0.0.1:8000/db/", data=def_dict, auth=get_auth_data())
        # проверяем успешность запроса
        if resp.status_code == 201:
            counter_ok += 1
        else:
            counter_err += 1
        total += 1
        # каждые 5 статей выводим информацию о прогрессе
        if total % 5 == 0:
            print("\rAdding articles: %s successful, %s unsuccessful%s" % (
                counter_ok, counter_err, getProgress(total / 5 % 3 + 1)),
                  end='', flush=True)
    time.sleep(0.5)
    print("\rFinished adding articles: %s successful, %s unsuccessful" % (counter_ok, counter_err), end='', flush=True)

# Удалить все отзывы
def delete_feedback():
    # подтверждение
    if not confirm():
        print("Cancelled by user")
        return
    # получаем список статей
    feedback = requests.get("http://127.0.0.1:8000/db/feedback/")
    # проверяем успешность запроса
    if feedback.status_code != 200:
        print("Database unreachable")
        return
    # парсим данные в json
    feedback = feedback.json()
    # считаем количество отзывов
    counter = 0
    for feed in feedback:
        counter += 1
    current_counter = 1
    print("Starting...")
    # итерируемся по всем отзывам
    for feed in feedback:
        # удаляем отзыв по id
        resp_delete = requests.delete("http://127.0.0.1:8000/db/feedback/%s/" % feed['id'], auth=get_auth_data())
        # проверяем успешность запроса
        if resp_delete.status_code != 204:
            print("Deletion error")
            return
        # формируем строку с информацией о прогрессе
        line = "\rDeleting: %s of %s" % (current_counter, counter)
        # каждые 5 отзывов выводим информацию
        if current_counter % 5 == 0:
            print(line, end='', flush=True)
        current_counter += 1
    time.sleep(1)
    print("\rFinished, deleted %s feedback entries" % counter)

# просмотр таблицы инвайтов
def view_invites():
    resp = requests.get("http://127.0.0.1:8000/db/invites/")
    for invite in resp.json():
        print("Invite code: %s, email: %s" % (invite["invite"], invite["email"]))

# очистка таблицы инвайтов
def delete_invites():
    # подтверждение
    if not confirm():
        print("Cancelled by user")
        return
    # получаем список инвайтов
    resp = requests.get("http://127.0.0.1:8000/db/invites/")
    print("Starting...")
    counter = 0
    # удаляем инвайты и считаем их количество
    for invite in resp.json():
        requests.delete("http://127.0.0.1:8000/db/invites/%s/" % invite["id"], auth=get_auth_data())
        counter += 1
    print("Finished, deleted %s invites" % counter)

# подтверждение удаления
def confirm():
    in_word = input("To confirm - type \"delete\":  ")
    return in_word == "delete"

# словарь функций
options = {
    1: delete_users,
    2: make_users_file,
    3: load_users_file,
    4: delete_articles,
    5: make_articles_file,
    6: load_articles_file,
    7: delete_feedback,
    8: delete_invites,
    9: view_invites
}
if __name__ == '__main__':
    while True:
        # печатаем разделитель
        print()
        print("_" * 100)
        # ожидаем ввод номера функции
        select = input(
            "\nWelcome to database management interface. Select action:\n1)Delete users 2)Save users as file 3)Load users from file\n4)Delete articles 5)Save articles as file 6)Load articles from file\n7)Delete feedback\n8)Clear invite table 9)View invite table\nEnter number:")
        # обрабатываем ввод
        try:
            select = int(select)
        except:
            print("Wrong input")
            continue
        # проверям доступность функции по номеру
        if select <= 9 and select >= 1:
            # вызываем функцию
            options[select]()
        else:
            print("Wrong command")
