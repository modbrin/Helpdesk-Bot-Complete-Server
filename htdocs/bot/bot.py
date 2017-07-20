# -*- coding: utf-8 -*-
import telebot
import logging
import time
from config import *
from utils import *
from ticketCreator import createTicket, createTicketWithAtt, addComment, addAttachment
from bot_db_interface import *
import sys
import copy
from NLP_client import get_token_array
from tickets_worker import getAllTickets, getClosedTickets, getOpenedTickets, getTicketById, get_user_att, get_sw_att
import requests
from keycode_validator import confirm_keycode, send_validation

bot = telebot.TeleBot(token)

# инициализация логгеров
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr = logging.FileHandler('bot_logs.log')
hdlr.setFormatter(formatter)
telebot.logger.addHandler(hdlr)
logger = logging.getLogger('bot_logger')
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)


# states:
# 1 - начальное состояние
# 2 - состояние написания отзыва
# 3 - состояние написания нового вопроса
# 4 - состояние написания комментария, вложения к тикету


# список, который будет хранить user_id зарегистрированных пользователей
known_users = []
# словарь, который хранит язык для определённого пользователя по ключу user_id
langs = {}
# словарь, который хранит состояние определённого пользоателя по ключу user_id
states = {}
# словарь, который хранит последний выбранный юзером ticket_id определённого пользоателя по ключу user_id
ticket_ids = {}
# словарь, который хранит сообщение, которое пользователь хочет отправить по ключу user_id
messages = {}
# словарь, который хранит file_id вложений, которое пользователь хочет отправить по ключу user_id
attachments = {}


# функция для того, чтобы узнавать зарегистрирован ли пользователь
def is_uid_exists(uid):
    if uid in known_users:
        return True
    elif uid_exists(uid):
        known_users.append(uid)
        return True
    else:
        return False


# фунцкия для того, чтобы получить предпочитаемый язык пользователя
def get_lang_local(uid):
    if uid in langs.keys():
        return langs[uid]
    lang = get_lang(uid)
    if lang is None:
        return 'EN'
    else:
        langs[uid] = lang
        return lang


# функция для получения состояния пользователя
def get_state_local(uid):
    if uid in states.keys():
        return states[uid]
    state = get_state(uid)
    if state:
        states[uid] = state
        return state
    else:
        return 1


# функция для получения текста сообщений
def get_message_text(uid):
    if uid in messages.keys():
        return messages[uid] 
    message = get_message_text(uid)
    if message: 
        messages[uid] = message
        return message 
    else:
        return ''


# функция для получения списка file_id вложений
def get_attachments(uid):
    if uid in attachments.keys():
        return attachments[uid]
    atts = get_message_att(uid)
    if atts:
        attachments[uid] = atts
        return atts
    else:
        return []


# функция для получения ticket_id, к которому пользователь хочет написать ответ
def get_ticket_id_local(uid):
    if uid in ticket_ids.keys():
        return ticket_ids[uid]
    ticket_id = get_ticket_id(uid)
    if ticket_id:
        ticket_ids[uid] = ticket_id
    return ticket_id


# функция для обработки кнопки отправить вопрос
def handle_send_button(user_id, chat_id):
    text = get_message_text(user_id)
    attachments = get_attachments(user_id)
    state = get_state_local(user_id)
    mail = get_email(user_id)
    is_articles = False
    if state == 3:
        articles = get_article_list(get_token_array(text))
        if articles:
            is_articles = True
            data = []
            lang = get_lang_local(user_id)
            if lang == 'EN':
                data.append(list_of_articles_eng)
            else:
                data.append(list_of_articles_ru)
            data.append('\n\n')
            for key, value in articles.items():
                data.extend([key, ': \n', value, '\n\n'])
            letter = ''.join(data)
            write_message(text_eng=letter, text_rus=letter, lang=lang, markup_eng=ans_markup_eng,
                        markup_rus=ans_markup_rus, chat_id=chat_id)
        else:
            send_question_to_sw(text, no_articles_rus, no_articles_eng, user_id, chat_id, attachments)
    elif state == 4:
        ticket_id = get_ticket_id_local(user_id)
        send_question_to_sw(text, success_comment_rus, success_comment_eng, user_id, chat_id, attachments, ticket_id)

    if not is_articles:
        set_to_initial_and_clear(user_id)
        print_to_log_question(text, mail)


# обрабатывает команду /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    if not get_chat_id(user_id):
        logger.debug('\n' + 'New user: ' + message.from_user.username + '\n')
        set_chat_id(user_id, message.chat.id)

    # если пользователя нет в базе, то просим его ввести свою почту
    if not is_uid_exists(user_id):
        bot.send_message(message.chat.id, write_mail, reply_markup=contacts_markup)
    # выводим это сообщение, если бот уже знает человека
    else:
        write_message(text_eng=known_eng, text_rus=known_rus, chat_id=message.chat.id,
                      markup_rus=menu_markup_rus, markup_eng=menu_markup_eng,
                      lang=get_lang_local(user_id))


# обрабатывает кнопку контакты
@bot.message_handler(func=lambda message: message.text in [contacts_eng, contacts_rus])
def handle_contacts(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    contact_info = get_contact_info()
    if is_uid_exists(user_id):
        write_message(text_eng=contact_info, text_rus=contact_info, chat_id=chat_id,
        lang=get_lang_local(user_id), markup_eng=menu_markup_eng, markup_rus=menu_markup_rus)
    else:
        bot.send_message(chat_id, contact_info, reply_markup=contacts_markup)


# обрабатывает ввод почты
@bot.message_handler(func=lambda message: not is_uid_exists(message.from_user.id) and message.text 
                                            and not message.text.isdigit())
def handle_mail(message):
    if is_email(message.text) and is_inno_email(message.text):
        mail = cut_domain(message.text)
        bot.send_message(message.chat.id, send_confirmation, reply_markup=contacts_markup)
        send_validation(mail, message.from_user.id)
    else:
        bot.send_message(message.chat.id, wrong_format, reply_markup=contacts_markup)


# обрабатывает ввод кода
@bot.message_handler(func=lambda message: not is_uid_exists(message.from_user.id) and message.text 
                                            and message.text.strip().isdigit())
def handle_code(message):
    code = message.text.strip()
    ans = confirm_keycode(message.from_user.id, message.chat.id, code)
    if ans == 'limit':
        bot.send_message(message.chat.id, repeat_code, reply_markup=contacts_markup)
    elif ans:
        hello_message(message.from_user, message.chat.id)
    else:
        bot.send_message(message.chat.id, wrong_code, reply_markup=contacts_markup)        


# обрабатывает кнопку отмена
@bot.message_handler(func=lambda message: is_uid_exists(message.from_user.id)
                    and message.text in [cancel_eng, cancel_rus])
def handle_cancel_button(message):
    user_id = message.from_user.id
    set_state(user_id, 1)  # изменяем состояние на изначальное
    states[user_id] = 1
    clear_message_content(user_id)
    messages[user_id] = ''
    clear_message_att(user_id)
    if user_id in attachments.keys(): del attachments[user_id]
    write_message(text_eng=operation_cancelled_eng, text_rus=operation_cancelled_rus,
                  lang=get_lang_local(message.from_user.id), markup_eng=menu_markup_eng,
                  markup_rus=menu_markup_rus, chat_id=message.chat.id)


@bot.message_handler(func=lambda message: is_uid_exists(message.from_user.id) and
                                        get_state_local(message.from_user.id) == 2, content_types=['text'])
def handle_feedback(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    mail = get_email(user_id)
    newFeedback(message.from_user.first_name + ' ' + message.from_user.last_name,
                mail, str(get_rating(user_id)), message.text)
    write_message(text_eng=success_feedback_eng, text_rus=success_feedback_rus,
                  lang=get_lang_local(user_id), markup_eng=menu_markup_eng,
                  markup_rus=menu_markup_rus, chat_id=chat_id)
    logger.debug('\n' + 'New feedback from ' + mail + ': ' + message.text + '\n')
    set_state(user_id, 1)
    states[user_id] = 1


@bot.message_handler(func=lambda message: is_uid_exists(message.from_user.id) and
                                        get_state_local(message.from_user.id) == 2)
def handle_wrong_feedback(message):
    # говорим пользователю, что в отзывах можно писать только текст
    write_message(text_eng=no_text_message_eng, text_rus=no_text_message_rus,
                  lang=get_lang_local(user_id), markup_eng=cancel_markup_eng,
                  markup_rus=cancel_markup_rus, chat_id=message.chat.id)


# обрабатывает кнопку нашёл ответ в статье
@bot.message_handler(func=lambda message: is_uid_exists(message.from_user.id)
                    and message.text in [ans_found_eng, ans_found_rus]
                    and get_state_local(message.from_user.id) in [3, 4])
def handle_ans_found(message):
    user_id = message.from_user.id
    set_to_initial_and_clear(user_id)
    write_message(text_eng=happy_eng, text_rus=happy_rus,
                  chat_id=message.chat.id, lang=get_lang_local(user_id),
                  markup_eng=menu_markup_eng, markup_rus=menu_markup_rus)


# обрабатывает кнопку не нашёл ответ в статье
@bot.message_handler(func=lambda message: is_uid_exists(message.from_user.id)
                    and message.text in [ans_not_found_eng, ans_not_found_rus]
                    and get_state_local(message.from_user.id) in [3, 4])
def handle_ans_not_found(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = get_message_text(user_id)
    attachments = get_attachments(user_id)
    send_question_to_sw(text, success_issue_rus, success_issue_eng, user_id, chat_id, attachments)
    set_to_initial_and_clear(user_id)


# обрабатывает кнопку добавить вложения, текст
@bot.message_handler(func=lambda message: is_uid_exists(message.from_user.id)
                    and message.text in [add_eng, add_rus]
                    and get_state_local(message.from_user.id) in [3, 4])
def handle_add_new(message):
    write_message(text_eng=add_more_eng, text_rus=add_more_rus,
                  chat_id=message.chat.id, lang=get_lang_local(message.from_user.id),
                  markup_eng=cancel_markup_eng, markup_rus=cancel_markup_rus)


# обрабатывает новые сообщения в состояниях, отличных от изначального и сохраняет их в базу данных
@bot.message_handler(func=lambda message: is_uid_exists(message.from_user.id) and
                        get_state_local(message.from_user.id) in [3, 4], content_types=['text'])
def handle_write_of_message(message):
    user_id = message.from_user.id
    add_message_content(user_id, message.text)
    messages[user_id] = (messages.get(user_id, '') + ' ' + message.text).strip()
    write_message(text_eng=send_or_add_eng, text_rus=send_or_add_rus,
                  chat_id=message.chat.id, lang=get_lang_local(user_id),
                  markup_eng=send_markup_eng, markup_rus=send_markup_rus)


# обрабатывает вложения и сохраняет их в базу данных
@bot.message_handler(func=lambda message: is_uid_exists(message.from_user.id) and
                        get_state_local(message.from_user.id) in [3, 4], content_types=['photo', 'document'])
def handle_write_of_attachment(message):
    user_id = message.from_user.id
    if message.document:
        file_id = message.document.file_id
    else:
        # берём фото с наибольшим разрешением
        photo = message.photo[len(message.photo) - 1]
        file_id = photo.file_id
    add_message_att(user_id, file_id)
    attachments[user_id] = attachments.get(user_id, [])
    attachments[user_id].append(file_id)
    write_message(text_eng=send_or_add_eng, text_rus=send_or_add_rus,
                  chat_id=message.chat.id, lang=get_lang_local(user_id),
                  markup_eng=send_markup_eng, markup_rus=send_markup_rus)


# обрабатывает кнопку изменения языка
@bot.message_handler(func=lambda message: is_uid_exists(message.from_user.id)
                    and message.text in [change_lang_eng, change_lang_rus])
def handle_change_lang(message):
    user_id = message.from_user.id
    lang = get_lang_local(user_id)
    if lang == 'EN':
        set_lang_ru(user_id)
        langs[user_id] = 'RU'
        bot.send_message(message.chat.id, lang_changed_rus, reply_markup=menu_markup_rus)
    else:
        set_lang_en(user_id)
        langs[user_id] = 'EN'
        bot.send_message(message.chat.id, lang_changed_eng, reply_markup=menu_markup_eng)


# обрабатывает кнопку оценить бота
@bot.message_handler(func=lambda message: is_uid_exists(message.from_user.id)
                    and message.text in [feedback_eng, feedback_rus])
def handle_feedback(message):
    user_id = message.from_user.id
    write_message(text_eng=grade_eng, text_rus=grade_rus,
                  chat_id=message.chat.id, lang=get_lang_local(user_id),
                  markup_eng=grade_markup_eng, markup_rus=grade_markup_rus)


# обрабатывает кнопку написать новый вопрос
@bot.message_handler(func=lambda message: is_uid_exists(message.from_user.id)
                    and message.text in [issue_eng, issue_rus])
def handle_question(message):
    user_id = message.from_user.id
    set_state(user_id, 3)
    states[user_id] = 3
    write_message(text_eng=write_issue_eng, text_rus=write_issue_rus,
                  chat_id=message.chat.id, lang=get_lang_local(user_id),
                  markup_eng=cancel_markup_eng, markup_rus=cancel_markup_rus)
    clear_message_content(user_id)
    messages[user_id] = ''
    clear_message_att(user_id)
    if user_id in attachments.keys(): del attachments[user_id]


# обрабатывает кнопку мои вопросы
@bot.message_handler(func=lambda message: is_uid_exists(message.from_user.id)
                    and message.text in [tickets_eng, tickets_rus])
def handle_my_questions(message):
    write_message(text_rus=tickets_section_rus, text_eng=tickets_section_eng,
                  lang=get_lang_local(message.from_user.id), markup_rus=tickets_markup_rus,
                  markup_eng=tickets_markup_eng, chat_id=message.chat.id)


# получение диалога в тикете по id
@bot.message_handler(func=lambda message: message.text and message.text[0] == '/' and len(message.text) > 1
                                          and message.text[1:].isdigit())
def handle_getting_ticket(message):
    ticket_id = int(message.text[1:])
    chat_id = message.chat.id
    all_ids = getAllTickets(get_email(message.from_user.id))
    # проверяем, что пользователь пытается посмотреть свой тикет, иначе выводим сообщение,
    # что он пытается посмотреть чужой тикет
    if ticket_id in all_ids:
        user_id = message.from_user.id
        lang = get_lang_local(user_id)
        data = list(getTicketById(ticket_id).items())
        if lang == 'EN':
            text_builder = [conver_id_eng.format(id=ticket_id) + '\n\n', question_eng + data[0][0] + '.\n\n']
        else:
            text_builder = [conver_id_rus.format(id=ticket_id) + '\n\n', question_rus + data[0][0] + '.\n\n']

        # вложения пользователя
        user_doc_att, user_photo_att = get_user_att(ticket_id)
        # вложения из sw
        sw_doc_att, sw_photo_att = get_sw_att(ticket_id)

        dialogue = data[0][1]
        if dialogue:
            for temp in dialogue:
                if temp != 'Attachment:' and temp != 'Получено новое вложение':
                    text_builder.extend(['➡ ', temp, '\n'])
            text = ''.join(text_builder)
            if ticket_id not in getClosedTickets(get_email(user_id)):
                markup_eng = inline_add_comment_eng
                markup_rus = inline_add_comment_rus
            else:
                markup_eng = menu_markup_eng
                markup_rus = menu_markup_rus
            write_message(text_eng=text, text_rus=text,
                          chat_id=chat_id, lang=get_lang_local(user_id),
                          markup_eng=markup_eng, markup_rus=markup_rus)
            if user_doc_att or user_photo_att or sw_photo_att or sw_doc_att:
                write_message(text_eng=att_eng, text_rus=att_rus,
                              chat_id=chat_id, lang=get_lang_local(user_id),
                              markup_eng=menu_markup_eng, markup_rus=menu_markup_rus)
                for file_id in user_photo_att:
                    bot.send_chat_action(chat_id, 'upload_photo')
                    bot.send_photo(chat_id, file_id)
                for file_id in user_doc_att:
                    bot.send_chat_action(chat_id, 'upload_document')
                    bot.send_document(chat_id, file_id)
                for path in sw_photo_att:
                    bot.send_chat_action(chat_id, 'upload_photo')
                    bot.send_photo(chat_id, open(path, 'rb'))
                for path in sw_doc_att:
                    bot.send_chat_action(chat_id, 'upload_document')
                    bot.send_document(chat_id, open(path, 'rb'))

        if not dialogue:
            write_message(text_eng=no_dialogue_eng, text_rus=no_dialogue_rus,
                          chat_id=get_chat_id(message.from_user.id), lang=get_lang_local(message.from_user.id),
                          markup_eng=menu_markup_eng, markup_rus=menu_markup_rus)
    else:
        write_message(text_eng=not_your_question_eng, text_rus=not_your_question_rus,
                      chat_id=get_chat_id(message.from_user.id), lang=get_lang_local(message.from_user.id),
                      markup_eng=menu_markup_eng, markup_rus=menu_markup_rus)


# обрабатывает оставшиеся сообщения
@bot.message_handler(func=lambda message: True)
def handle_remain_message(message):
    bot.send_message(message.chat.id, tap_to_start)


# обрабатывает нажатие на inline кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    data = call.data
    if call.message:
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        if data in ['all', 'opened', 'closed']:
            if data == 'all':
                tickets = getAllTickets(get_email(user_id))
            elif data == 'closed':
                tickets = getClosedTickets(get_email(user_id))
            else:
                tickets = getOpenedTickets(get_email(user_id))
            if tickets:
                write_issues(tickets, chat_id, user_id, data)
            else:
                text_eng = ''
                text_rus = ''
                if data == 'all':
                    text_eng = no_tickets_eng
                    text_rus = no_tickets_rus
                elif data == 'opened':
                    text_eng = no_opened_tickets_eng
                    text_rus = no_opened_tickets_rus
                elif data == 'closed':
                    text_eng = no_closed_tickets_eng
                    text_rus = no_closed_tickets_rus
                write_message(text_eng=text_eng, text_rus=text_rus,
                              chat_id=chat_id, lang=get_lang_local(user_id),
                              markup_eng=menu_markup_eng, markup_rus=menu_markup_rus)
        elif data in ['1', '2', '3', '4', '5']:
            set_rating(user_id, data)
            edit_message(call.message, get_lang_local(user_id), data, call.from_user.first_name,
                         call.from_user.last_name, user_id)
        elif data == 'feedback':
            set_state(user_id, 2)
            states[user_id] = 2
            write_message(text_eng=write_feedback_eng, text_rus=write_feedback_rus,
                          chat_id=chat_id, lang=get_lang_local(user_id),
                          markup_eng=cancel_markup_eng, markup_rus=cancel_markup_rus)
        elif data == 'add_comment':
            clear_message_content(user_id)
            messages[user_id] = ''
            clear_message_att(user_id)
            if user_id in attachments.keys(): del attachments[user_id]
            set_state(user_id, 4)
            states[user_id] = 4
            text = call.message.text
            ticket_id = get_ticket_id_from_text(text)
            set_ticket_id(user_id, ticket_id)
            ticket_ids[user_id] = ticket_id
            write_message(text_eng=write_comment_eng, text_rus=write_comment_rus,
                          chat_id=chat_id, lang=get_lang_local(user_id),
                          markup_eng=cancel_markup_eng, markup_rus=cancel_markup_rus)
        elif data == 'send':
            handle_send_button(user_id, chat_id)
        elif data == 'add_more':
            write_message(text_rus=add_more_rus, text_eng=add_more_eng,
                          lang=get_lang_local(user_id), markup_rus=cancel_markup_rus,
                          markup_eng=cancel_markup_eng, chat_id=chat_id)
        bot.answer_callback_query(call.id)


# выводит пользователю список тикетов
def write_issues(data, chat_id, user_id, type):
    lang = get_lang_local(user_id)
    text_builder = []
    if lang == 'EN':
        if type == 'all':
            text_builder.append(all_conv_eng)
        elif type == 'opened':
            text_builder.append(opened_conv_eng)
        elif type == 'closed':
            text_builder.append(closed_conv_eng)
    else:
        if type == 'all':
            text_builder.append(all_conv_rus)
        elif type == 'opened':
            text_builder.append(opened_conv_rus)
        elif type == 'closed':
            text_builder.append(closed_conv_rus)
    text_builder.append('\n\n')
    for key, value in data.items():
        text_builder.extend(['🔘 ', value, ': ', '/' + str(key), '\n\n'])
    text = ''.join(text_builder)
    write_message(text_eng=text, text_rus=text,
                chat_id=chat_id, lang=get_lang_local(user_id),
                markup_eng=menu_markup_eng, markup_rus=menu_markup_rus)


# функция для написания сообщения пользователю
def write_message(text_eng, text_rus, chat_id, lang, markup_eng, markup_rus):
    if lang == 'EN':
        bot.send_message(chat_id, text_eng, reply_markup=markup_eng)
    else:
        bot.send_message(chat_id, text_rus, reply_markup=markup_rus)


# отправляет вопрос в spicework и отвечает пользователю
def send_question_to_sw(text, text_rus, text_eng, user_id, chat_id, att=None, ticket_id=None):
    write_message(text_eng=text_eng, text_rus=text_rus,
                  lang=get_lang_local(user_id), markup_eng=menu_markup_eng,
                  markup_rus=menu_markup_rus, chat_id=chat_id)
    # создаёт новый тикет в spicework
    if not ticket_id:
        email = get_email(user_id)
        if not att:
            createTicket(text, email)
        else:
            files, extensions = get_files(att)
            for i in range(len(att)):
                att[i] = att[i] + extensions[i]
            createTicketWithAtt(text, email, files, att)
    # отправляет вопрос по ticket id
    else:
        if text != 'null':
            addComment(text, ticket_id)
        if att:
            files, extensions = get_files(att)
            for i in range(len(att)):
                att[i] = att[i] + extensions[i]
            for i in range(len(files)):
                addAttachment(files[i], ticket_id, att[i])


# редактирует кнопки под сообщением оценки
def edit_message(message, lang, number, first_name, last_name, user_id):
    if lang == 'EN':
        new_keyboard = copy.deepcopy(grade_markup_eng)
    else:
        new_keyboard = copy.deepcopy(grade_markup_rus)

    # изменяем выбранную оценку, чтобы можно было определить какую оценку поставили
    new_keyboard.to_dic()['inline_keyboard'][0][int(number) - 1]['text'] = '⭐ ' + number
    new_keyboard.to_dic()['inline_keyboard'][0][int(number) - 1]['callback_data'] = 'changed'

    newFeedback(first_name + ' ' + last_name, get_email(user_id), number, '')

    bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id,
                                  reply_markup=new_keyboard)


def hello_message(user, chat_id):
    name_of_user = user.first_name
    bot.send_message(chat_id,
                     'Hi, {name}. I am glad to see you. Here you can ask technical '
                     'questions addressed to the IT department.'.format(name=name_of_user),
                     reply_markup=menu_markup_eng)
    set_state(user.id, 1)
    states[user.id] = 1
    set_lang_en(user.id)
    langs[user.id] = 'EN'
    logger.debug('\n' + 'New user: @' + user.username + '\n')


# функция для извлечения ticket id из сообщения
def get_ticket_id_from_text(text):
    index = text.find('id')
    # индекс, с которого начинается id
    start = text.find(':', index) + 3
    # индекс, на котором заканичивается id
    end = text.find('.', start)
    return text[start:end]


# функция для получения файлов и их расширений
def get_files(attachment_ids):
    files = []
    extensions = []
    for file_id in attachment_ids:
        file_info = bot.get_file(file_id)
        # из пути файла достаю его расширение
        extensions.append(file_info.file_path[file_info.file_path.rindex('.'):])
        response = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))
        if response.status_code == requests.codes.ok:
            files.append(response.content)
    return files, extensions


def print_to_log_question(text, mail):
    if text != 'null':
        logger.debug('\n' + 'New question from ' + mail + ' : ' + text + '\n')
    else:
        logger.debug('\n' + 'New question from ' + mail + ' : (attachment)' + '\n')


def set_to_initial_and_clear(user_id):
    set_state(user_id, 1)
    states[user_id] = 1
    clear_message_att(user_id)
    if user_id in attachments.keys(): del attachments[user_id]
    clear_message_content(user_id)
    messages[user_id] = ''

if __name__ == "__main__":
    while True:
        try:
            bot.polling()
        except Exception as e:
            logger.warning(e)
            print(e)
            logger.warning("Error occured, retry in 10 seconds")
            print("Error occured, retry in 10 seconds")
        time.sleep(10)