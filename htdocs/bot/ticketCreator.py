import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email_params import get_config

def createTicket(message, email):
    if not message:
        message = "(empty question)"
    # составляем текст письма
    cc = get_config('cc_mailbox.txt')
    receiver = get_config('incoming_email.txt')
    sender, password, host, port = get_config('outgoing_email.txt')
    body = message
    if "@innopolis.ru" not in email:
        email = email.strip() + "@innopolis.ru"
    # добавляем необходимые теги
    body += "\n\n#creator " + email + "\n#cc " + cc[0]
    # назначаем отправителя, адрес которого указан в sw и в outgoing email
    fromaddr = sender
    # получаетель = почта, которая указана в sw в разделе incoming email (также указана в incoming email)
    toaddr = receiver[0]
    # собираем объект письма
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'Ticket from "{}": '.format(email) + message[0:15]
    if(len(message)>15):
        msg['Subject'] += '...'
    msg.attach(MIMEText(body, 'plain'))
    # подключаемся к smtp серверу Google
    server = smtplib.SMTP(host, port)
    server.starttls()
    # проводим авторизацию
    server.login(fromaddr, password)
    # переводим сообщение в текст
    text = msg.as_string()
    # отправляем письмо
    server.sendmail(fromaddr, toaddr, text)
    # закрываем соединение
    server.quit()

#создает тикет и добавляет к нему вложения
def createTicketWithAtt(message, email, attList, nameList):
    if not message:
        message = "(empty question)"
    # составляем текст письма
    cc = get_config('cc_mailbox.txt')
    receiver = get_config('incoming_email.txt')
    sender, password, host, port = get_config('outgoing_email.txt')
    body = message
    if "@innopolis.ru" not in email:
        email = email.strip() + "@innopolis.ru"
    # добавляем необходимые теги
    body += "\n\n#creator " + email + "\n#cc " + cc[0]
    # назначаем отправителя, адрес которого указан в sw и в outgoing email
    fromaddr = sender
    # получаетель = почта, которая указана в sw в разделе incoming email (также указана в incoming email)
    toaddr = receiver[0]
    # собираем объект письма
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'Ticket from "{}": '.format(email) + message[0:15]
    if(len(message)>15):
        msg['Subject'] += '...'
    msg.attach(MIMEText(body, 'plain'))
    #добавляет к письму вложения
    for attachment in attList:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition','attachment', filename = nameList[attList.index(attachment)])
        msg.attach(part)
    # подключаемся к smtp серверу Google
    server = smtplib.SMTP(host, port)
    server.starttls()
    # проводим авторизацию
    server.login(fromaddr, password)
    # переводим сообщение в текст
    text = msg.as_string()
    # отправляем письмо
    server.sendmail(fromaddr, toaddr, text)
    # закрываем соединение
    server.quit()

def addComment(message, ticket_id):
    # составляем текст письма
    # получаем информацию о почтовых ящиках
    receiver= get_config('incoming_email.txt')
    sender, password, host, port = get_config('outgoing_email.txt')
    body = message
    # назначаем отправителя, адрес которого указан в sw и в outgoing email
    fromaddr = sender
    # получаетель = почта, которая указана в sw в разделе incoming email (также указана в incoming email)
    toaddr = receiver[0]
    # собираем объект письма
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = '[Ticket #' + str(ticket_id) + '] new ticket'
    msg.attach(MIMEText(body, 'plain'))
    # подключаемся к smtp серверу Google
    server = smtplib.SMTP(host, port)
    server.starttls()
    # проводим авторизацию
    server.login(fromaddr, password)
    # переводим сообщение в текст
    text = msg.as_string()
    # отправляем письмо
    server.sendmail(fromaddr, toaddr, text)
    # закрываем соединение
    server.quit()

def addAttachment(attachment, ticket_id, att_name):
    # составляем текст письма
    # получаем информацию о почтовых ящиках
    receiver = get_config('incoming_email.txt')
    sender, password, host, port = get_config('outgoing_email.txt')
    body = 'Получено новое вложение'
    # назначаем отправителя, адрес которого указан в sw и в outgoing email
    fromaddr = sender
    # получаетель = почта, которая указана в sw в разделе incoming email (также указана в incoming email)
    toaddr = receiver[0]
    # собираем объект письма
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = '[Ticket #' + str(ticket_id) + '] new ticket'
    msg.attach(MIMEText(body, 'plain'))
    #добавляет к письму вложение
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition','attachment', filename = att_name)
    msg.attach(part)
    # подключаемся к smtp серверу Google
    server = smtplib.SMTP(host, port)
    server.starttls()
    # проводим авторизацию
    server.login(fromaddr, password)
    # переводим сообщение в текст
    text = msg.as_string()
    # отправляем письмо
    server.sendmail(fromaddr, toaddr, text)
    # закрываем соединение
    server.quit()
