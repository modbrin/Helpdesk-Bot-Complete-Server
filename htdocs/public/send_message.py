import telebot
import sys
sys.path.append('..\\bot')
from bot_db_interface import *
from utils import *

def send_hello_message(user_id, chat_id):
    bot = telebot.TeleBot('363385669:AAHadMpKkzi4bWNeDbTPL-dOZtACtO98CsQ')
    bot.send_message(chat_id,
                     'Hi! I am glad to see you. Here you can ask technical '
                     'questions addressed to the IT department.',
                     reply_markup=menu_markup_eng)
    set_state(user.id, 1)
    set_lang_en(user.id)
