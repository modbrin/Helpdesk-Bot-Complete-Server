# This script is example code from this blog post:
# http://www.voidynullness.net/blog/2013/07/25/gmail-email-with-python-via-imap/
#
# This is an updated version of the original -- modified to work with Python 3.4.
#
import sys
import os
import imaplib
import email
import quopri
import email
import email.header
import datetime
from bot_db_interface import *
from send_message import send_question_assign, send_answer, send_notification, send_attachment
import time
from email_params import get_config
from bot_db_interface import cut_domain
import glob


# Поиск идет в INBOX
EMAIL_FOLDER = "INBOX"

#обрабатывет непрочитанные входящие письма от IT departament(в настройках Spiceworks так указано имя отправителя)
def process_mailbox(M):
    try:
        rv, data = M.search(None, '(UNSEEN)','(FROM "IT department")')
        #закончить выполнение при отсутствии писем
        if rv != 'OK':
            print("Empty")
            return
    except imaplib.IMAP4.error:
        print("ERROR: search failed")
        return
    for num in data[0].split():
        try:
            rv, data = M.fetch(num, '(RFC822)')
            if rv != 'OK':
                print("ERROR getting message", num)
                return
        except imaplib.IMAP4.error:
            print("ERROR: fetch failed")
            return
        #  msg кладется содержимое письма в виде строки
        try:
            msg = email.message_from_bytes(data[0][1])
            # передает ключевую информацию из письма на вход #send_to_user
            parse_and_send(msg)
        except imaplib.IMAP4.error:
            print("ERROR: email parsing failed")
            return

def parse_and_send(message):
    counter = 0
    attachments = []
    #запоминаем текущую директорию
    start_path = os.getcwd() + '\\'
    path = start_path + 'attachments'+ '\\'
    #переходим в %start_path\attachments\
    os.chdir(path)
    # удаляем все старые файлы в папке
    files = glob.glob(path+'*')
    for f in files:
        os.remove(f)
    # собираем все новые файлы в список, сохраняя их временно в папку
    for part in message.walk():
        #обрабатываем вложения
        if(part.get_content_disposition()=='attachment'):
                #получаем полный путь к новому файлу
                filepath = '{}'+part.get_filename()
                filepath = filepath.format(path)
                attachments.append(filepath)
                #создаем файл
                f = open(part.get_filename(), 'wb')
                f.write(part.get_payload(decode=True))
                f.close()
    os.chdir(start_path)
    string = quopri.decodestring(str(message))
    string = string.decode('utf-8','ignore')
    user_add = get_config('outgoing_email.txt')[0]
    user_add = user_add[0:len(user_add)-1]
    to = get_from_email(string, "to")
    ticket_id = get_from_email(string, "id")
    ticket_body = get_from_email(string, "ticket_body")
    url = get_from_email(string, "url")
    #индекс подстроки, содержащей информацию по следующему событию
    prev_event = 0
    #в цикле обрабатывается ближайшее новое событие
    while(string.find("<!--event",prev_event)!=-1):
        prev_event = string.find("<!--event", prev_event)
        event_type = get_from_email(string,"event",prev_event)
        #обнуление дополнительных атрибутов, которые зависят от события
        comment_from = ""
        msg = ""
        if((event_type == "ticket-comment") or (event_type == "ticket-opened") or (event_type == "ticket-assigned")):
            msg=get_from_email(string,"msg",prev_event)
        if(event_type == "ticket-comment"):
            comment_from=get_from_email(string,"from", prev_event)
            #заканчиваем шаг цикла, если уведомление о комментарии пользователя
            if (comment_from == user_add or to == comment_from):
                prev_event+=1
                continue
        prev_event+=1
        #вызов функции, отправляющей уведомление пользователю с адресом = to, о событии = event_type (тикет открыт, закрыт, прокомментирован, привязан)
        #msg - пустая строка, если тикет открыт заново (event_type = ticket_reopened) или закрыт (event_type = ticket_closed)
        #если event_type = ticket_opened, то msg содержит запрос пользователя
        #если event_type = ticket_assigned, то msg содержит имя администратора, который отвечает за тикет и его почту
        #если event_type = ticket_comment, то comment_from содержит адрес комментатора (при других event_type остается пустым), а msg содержит текст комментария
        #функция send_to_user должна отправлять пользователю опощение, которое будет составлено с использованием перечисленных аргументов
        #(возможно, имеет смысл добавить к ней еще одним аргументом язык, на котором будут приходить оповещения)
        #send_to_user(to,event_type,id,comment_from,msg,attachments[],ticket_body)
        print("Got new message")
        is_finished = False
        # while (not is_finished):
        # try:
        user_id = get_uid(cut_domain(to))
        chat_id = get_chat_id(user_id)
        lang = get_lang(user_id)
        if not chat_id:
            print("Chat id not found for user "+to)
            continue
        msg = msg.rstrip()
        if msg == 'Attachment:':
            msg = '(attachment)'
        ticket_body = ticket_body.rstrip()
        if event_type == 'ticket-assigned':
            send_question_assign(chat_id, ticket_id, lang, msg, ticket_body)
            print('Message sent to bot')
        if event_type == 'ticket-comment' and attachments and msg:
            send_attachment(chat_id, lang, ticket_id, attachments, msg)
            print('Message sent to bot')
        elif event_type == 'ticket-comment' and msg:
            send_answer(chat_id, ticket_id, lang, msg)
            print('Message sent to bot')
        #ticket-opened
        #elif attachments:
            #send_attachment(chat_id, lang, ticket_id, attachments)
            #print('Message sent to bot')
        if event_type == 'ticket-closed':
            send_notification(chat_id, lang, ticket_id)
            print('Message sent to bot')
        is_finished = True
        #удаляем отправленные файлы
        # for file in attachments:
            # os.remove(file)
        # except:
            # print('Email parsing had been finished, but notification hasn\'t been sent')


#возвращает один из аргументов (to, id, msg, from(если комментарий), event_type), начиная поиск с last_ind (0, если не указано)
def get_from_email(text, arg, last_ind = 0):
    #вывод для проверки
    #print(arg,' = !',text[text.find("<!--"+arg+":",last_ind)+5+len(arg):text.find(":End_"+arg+"-->", last_ind)].replace('<br />','\n'),'!')
    return (text[text.find("<!--" + arg + ":", last_ind) + 5 + len(arg):text.find(":End_" + arg + "-->", last_ind)]).replace('<br />', '\n')

#запуск процесса, который обрабатывает сообщения, отправленные на указанный адрес
#второй аргумент - пароль от почты
def check_mailbox(email_account,password, host, port):
    try:
        M = imaplib.IMAP4_SSL(host, port)
        rv, data = M.login(email_account, password)
    except imaplib.IMAP4.error:
        print ("LOGIN FAILED!!! ")
        return
    try:
        rv, mailboxes = M.list()
        rv, data = M.select(EMAIL_FOLDER)
    except imaplib.IMAP4.error:
        print("ERROR: Unable to select email from mailbox")
        return
    if rv == 'OK':
        #запускает обработку сообщений в EMAIL_FOLDER
        process_mailbox(M)
        M.close()
    else:
        print("ERROR: Unable to open mailbox ", rv)
    M.logout()

# Запускаем проверку уведомлений, задержка 10 секунд
#считываем данные для подключения из файла, переданного на вход get_config
email_account, password, host, port = get_config('cc_mailbox.txt')
while True:
    try:
        check_mailbox(email_account, password, host, port)
    except Exception as e:
        print(e)
        print("Error occured, retry in 10 seconds")
    time.sleep(10)
