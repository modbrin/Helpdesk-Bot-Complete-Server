# -*- coding: utf-8 -*-
import config
from telebot import types

menu_markup_eng = types.ReplyKeyboardMarkup()
menu_markup_eng.row(config.issue_eng)
menu_markup_eng.row(config.feedback_eng, config.tickets_eng)
menu_markup_eng.row(config.contacts_eng, config.change_lang_eng)

menu_markup_rus = types.ReplyKeyboardMarkup()
menu_markup_rus.row(config.issue_rus)
menu_markup_rus.row(config.feedback_rus, config.tickets_rus)
menu_markup_rus.row(config.contacts_rus, config.change_lang_rus)

tickets_markup_eng = types.InlineKeyboardMarkup()
callback_button_all = types.InlineKeyboardButton(text=config.all_tickets_eng, callback_data="all")
callback_button_opened = types.InlineKeyboardButton(text=config.opened_tickets_eng, callback_data="opened")
callback_button_closed = types.InlineKeyboardButton(text=config.closed_tickets_eng, callback_data="closed")
tickets_markup_eng.add(callback_button_all)
tickets_markup_eng.add(callback_button_opened)
tickets_markup_eng.add(callback_button_closed)

tickets_markup_rus = types.InlineKeyboardMarkup()
callback_button_all = types.InlineKeyboardButton(text=config.all_tickets_rus, callback_data="all")
callback_button_opened = types.InlineKeyboardButton(text=config.opened_tickets_rus, callback_data="opened")
callback_button_closed = types.InlineKeyboardButton(text=config.closed_tickets_rus, callback_data="closed")
tickets_markup_rus.add(callback_button_all)
tickets_markup_rus.add(callback_button_opened)
tickets_markup_rus.add(callback_button_closed)

ans_markup_rus = types.ReplyKeyboardMarkup()
ans_markup_rus.add(config.ans_not_found_rus)
ans_markup_rus.add(config.ans_found_rus)
ans_markup_rus.add(config.add_rus)

ans_markup_eng = types.ReplyKeyboardMarkup()
ans_markup_eng.add(config.ans_not_found_eng)
ans_markup_eng.add(config.ans_found_eng)
ans_markup_eng.add(config.add_eng)

one_grade_button = types.InlineKeyboardButton(text='1', callback_data="1")
two_grade_button = types.InlineKeyboardButton(text='2', callback_data="2")
three_grade_button = types.InlineKeyboardButton(text='3', callback_data="3")
four_grade_button = types.InlineKeyboardButton(text='4', callback_data="4")
five_grade_button = types.InlineKeyboardButton(text='5', callback_data="5")

grade_markup_eng = types.InlineKeyboardMarkup()
add_comment_eng = types.InlineKeyboardButton(text=config.add_feedback_eng, callback_data='feedback')
grade_markup_eng.row(one_grade_button, two_grade_button, three_grade_button, four_grade_button, five_grade_button)
grade_markup_eng.add(add_comment_eng)

grade_markup_rus = types.InlineKeyboardMarkup()
add_comment_rus = types.InlineKeyboardButton(text=config.add_feedback_rus, callback_data='feedback')
grade_markup_rus.row(one_grade_button, two_grade_button, three_grade_button, four_grade_button, five_grade_button)
grade_markup_rus.add(add_comment_rus)


inline_add_comment_eng = types.InlineKeyboardMarkup()
inline_add_comment_eng.add(types.InlineKeyboardButton(text=config.add_eng, callback_data="add_comment"))


inline_add_comment_rus = types.InlineKeyboardMarkup()
inline_add_comment_rus.add(types.InlineKeyboardButton(text=config.add_rus, callback_data="add_comment"))


cancel_markup_eng = types.ReplyKeyboardMarkup()
cancel_markup_eng.row(config.cancel_eng)

cancel_markup_rus = types.ReplyKeyboardMarkup()
cancel_markup_rus.row(config.cancel_rus)

send_markup_rus = types.InlineKeyboardMarkup()
send_markup_rus.add(types.InlineKeyboardButton(text=config.send_rus, callback_data="send"))
send_markup_rus.add(types.InlineKeyboardButton(text=config.add_rus, callback_data="add_more"))

send_markup_eng = types.InlineKeyboardMarkup()
send_markup_eng.add(types.InlineKeyboardButton(text=config.send_eng, callback_data="send"))
send_markup_eng.add(types.InlineKeyboardButton(text=config.add_eng, callback_data="add_more"))

contacts_markup = types.ReplyKeyboardMarkup()
contacts_markup.row(config.contacts_eng)
