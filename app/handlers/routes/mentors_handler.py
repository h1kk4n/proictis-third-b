import os.path
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler

import app.web_functions
from config import Config
from app import dp


mentors_file_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '.data_mentors.json')
mentors_url = Config.BASE_URL + Config.url_path['mentors']


def form_mentors_list():

    mentors_json = app.web_functions.get_json_info(mentors_file_dir, mentors_url)

    message = '<b>Наставники Проектного офиса ИКТИБ:</b>\n\n'
    for mentor in mentors_json:
        message += f"-{ mentor['surname'] } { mentor['name'] } { mentor['patronymic'] }\n"
    message += f"\n<i>Источник</i>: { mentors_url.replace('/api', '') }"
    return message


def form_mentors_keyboard():

    mentors_json = app.web_functions.get_json_info(mentors_file_dir, mentors_url)

    new_keyboard_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=f"{mentor['surname']} {mentor['name']} {mentor['patronymic']}",
            callback_data=f"mentor: {mentor['surname']}"
        )] for mentor in mentors_json
    ] + [
        [InlineKeyboardButton(text='Назад', callback_data='mentors_return')]
    ])

    return new_keyboard_markup


def do_mentors(update, context):

    bot_message = form_mentors_list()

    keyboard_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Подробнее", callback_data='mentors_more'),
          InlineKeyboardButton(text='Закончить', callback_data='mentors_end')]]
    )

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=bot_message,
        reply_markup=keyboard_markup
    )


def more_mentors(update, context):

    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    new_keyboard_markup = form_mentors_keyboard()

    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text='<b>Наставники Проектного офиса ИКТИБ:</b>\n'
    )

    context.bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=new_keyboard_markup
    )


def find_mentor(update, context):

    query = update.callback_query

    mentors_json = app.web_functions.get_json_info(mentors_file_dir, mentors_url)

    founded_mentor = None
    bot_message = None
    surname = query.data.replace('mentor: ', '')
    for mentor in mentors_json:
        if surname == mentor['surname']:
            founded_mentor = mentor
            bot_message = f"{ mentor['surname'] } { mentor['name'] } { mentor['patronymic'] }\n\n" \
                          f"<u>Почта</u>: { mentor['email'] }\n" \
                          f"<u>Телефон</u>: { mentor['phone'] }\n" \
                          f"<u>Должность</u>: { mentor['post'] }\n" \
                          f"<u>Направление</u>: { mentor['directions'] }\n" \
                          f"\n<i>Источник</i>: { mentors_url.replace('/api', '') }"

    # deleting choice message
    context.bot.delete_message(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
    )

    keyboard_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Назад', callback_data='mentors_back'),
         InlineKeyboardButton(text='Закончить', callback_data='mentors_end')]
    ])
    context.bot.send_photo(
        chat_id=update.callback_query.message.chat_id,
        photo=founded_mentor['avatar']['link'],
        caption=bot_message,
        reply_markup=keyboard_markup
    )


def return_to_mentors_list(update, context):

    bot_message = form_mentors_list()

    keyboard_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Подробнее", callback_data='mentors_more'),
          InlineKeyboardButton(text='Закончить', callback_data='mentors_end')]]
    )

    context.bot.edit_message_text(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        text=bot_message
    )

    context.bot.edit_message_reply_markup(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=keyboard_markup
    )


def mentors_back(update, context):

    new_keyboard_markup = form_mentors_keyboard()

    context.bot.delete_message(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id
    )

    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        text='<b>Наставники Проектного офиса ИКТИБ:</b>\n',
        reply_markup=new_keyboard_markup
    )


def mentors_end(update, context):
    context.bot.edit_message_reply_markup(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=None
    )


dp.add_handler(CommandHandler(command='mentors', callback=do_mentors), group=0)
dp.add_handler(CallbackQueryHandler(callback=more_mentors, pattern='mentors_more'), group=0)
dp.add_handler(CallbackQueryHandler(callback=find_mentor, pattern=r'mentor: \D+'), group=0)
dp.add_handler(CallbackQueryHandler(callback=mentors_back, pattern='mentors_back'), group=0)
dp.add_handler(CallbackQueryHandler(callback=mentors_end, pattern='mentors_end'), group=0)
dp.add_handler(CallbackQueryHandler(callback=return_to_mentors_list, pattern='mentors_return'), group=0)
