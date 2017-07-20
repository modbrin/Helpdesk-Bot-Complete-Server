import telebot
from tickets_worker import *
from config import *
from utils import *

bot = telebot.TeleBot('363385669:AAHadMpKkzi4bWNeDbTPL-dOZtACtO98CsQ')


# метод для отправки сообщения о том, что вопрос прикреплён кому-то в sw
def send_question_assign(chat_id, ticket_id, lang, name, question):
    text_eng = ticket_assigned_eng.format(question=question, name=name, id=ticket_id)
    text_rus = ticket_assigned_rus.format(question=question, name=name, id=ticket_id)
    write_message(text_eng=text_eng, text_rus=text_rus, chat_id=chat_id, lang=lang,
                  markup_rus=inline_add_comment_rus, markup_eng=inline_add_comment_eng)


# метод для отправки ответа на вопрос
def send_answer(chat_id, ticket_id, lang, answer):
    text_eng = answer_eng.format(answer=answer, id=ticket_id)
    text_rus = answer_rus.format(answer=answer, id=ticket_id)
    write_message(text_eng=text_eng, text_rus=text_rus, chat_id=chat_id, lang=lang,
                  markup_rus=inline_add_comment_rus, markup_eng=inline_add_comment_eng)


# метод для отправки сообщения о том, что тикет закрыт
def send_notification(chat_id, lang, ticket_id):
    text_eng = ticket_closed_eng.format(id=ticket_id)
    text_rus = ticket_closed_rus.format(id=ticket_id)
    write_message(text_eng=text_eng, text_rus=text_rus, chat_id=chat_id, lang=lang,
                  markup_rus=menu_markup_rus, markup_eng=menu_markup_eng)


# метод для отправки вложения
def send_attachment(chat_id, lang, ticket_id, attachments, answer=''):
    text_eng = conver_id_eng.format(id=ticket_id) + '\n' + 'Answer to your question: ' + answer
    text_rus = conver_id_rus.format(id=ticket_id) + '\n' + 'Ответ на ваш вопрос: ' + answer
    if lang == 'EN':
        if not answer:
            text_eng = text_eng + '(attachment)'
        bot.send_message(chat_id, text_eng, reply_markup=inline_add_comment_eng)
        bot.send_message(chat_id, att_one_eng)
    else:
        if not answer:
            text_rus = text_rus + '(вложение)'
        bot.send_message(chat_id, text_rus, reply_markup=inline_add_comment_rus)
        bot.send_message(chat_id, att_one_rus)
    for path in attachments:
        if is_photo_attachment(path):
            bot.send_photo(chat_id, open(path, 'rb'))
        else:
            bot.send_document(chat_id, open(path, 'rb'))


# метод для написания сообщения пользователю
def write_message(text_eng, text_rus, chat_id, lang, markup_eng, markup_rus):
    if lang == 'EN':
        bot.send_message(chat_id, text_eng, reply_markup=markup_eng)
    else:
        bot.send_message(chat_id, text_rus, reply_markup=markup_rus)
