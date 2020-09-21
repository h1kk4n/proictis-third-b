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


def do_mentors(update, context):

    bot_message = '<b>Наставники Проектного офиса ИКТИБ:</b>\n'

    mentors_json = app.web_functions.get_json_info(mentors_file_dir, mentors_url)

    new_keyboard_markup = []

    for i in range(1, len(mentors_json), 2):
        l_col_mentor = mentors_json[i - 1]
        r_col_mentor = mentors_json[i]

        new_keyboard_markup.append(
            [InlineKeyboardButton(
                text=f"{l_col_mentor['surname']} {l_col_mentor['name'][0]} {l_col_mentor['patronymic'][0]}.",
                callback_data=f"mentor_show: {l_col_mentor['_id']}"
            ),
                InlineKeyboardButton(
                    text=f"{r_col_mentor['surname']} {r_col_mentor['name'][0]}. {r_col_mentor['patronymic'][0]}.",
                    callback_data=f"mentor_show: {r_col_mentor['_id']}"
                )]
        )

    if len(mentors_json) % 2 != 0:
        mentor = mentors_json[-1]
        new_keyboard_markup.append(
            [InlineKeyboardButton(
                text=f"{mentor['surname']} {mentor['name'][0]}. {mentor['patronymic'][0]}.",
                callback_data=f"mentor_show: {mentors_json[-1]['_id']}"
            )]
        )

    new_keyboard_markup.append(
        [InlineKeyboardButton(
            text='Оставить список наставников',
            callback_data='mentors_list_end'
        )]
    )

    query = update.callback_query

    if query is None:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=bot_message,
            reply_markup=InlineKeyboardMarkup(new_keyboard_markup)
        )
    else:
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=bot_message,
            reply_markup=InlineKeyboardMarkup(new_keyboard_markup)
        )


def find_mentor(update, context):

    query = update.callback_query

    mentors_json = app.web_functions.get_json_info(mentors_file_dir, mentors_url)

    founded_mentor = None
    bot_message = None
    mentor_id = query.data.replace('mentor_show: ', '')
    for mentor in mentors_json:
        if mentor_id == mentor['_id']:
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
    mentors_json = app.web_functions.get_json_info(mentors_file_dir, mentors_url)

    bot_message = '<b>Наставники Проектного офиса ИКТИБ:</b>\n\n'
    for mentor in mentors_json:
        bot_message += f"-{mentor['surname']} {mentor['name']} {mentor['patronymic']}\n"
    bot_message += f"\n<i>Источник</i>: {mentors_url.replace('/api', '')}"

    context.bot.edit_message_text(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        text=bot_message,
        reply_markup=None
    )


def mentors_end(update, context):
    context.bot.edit_message_reply_markup(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=None
    )


dp.add_handler(CommandHandler(command='mentors', callback=do_mentors), group=0)
dp.add_handler(CallbackQueryHandler(callback=find_mentor, pattern=r'mentor_show'), group=0)
dp.add_handler(CallbackQueryHandler(callback=do_mentors, pattern='mentors_back'), group=0)
dp.add_handler(CallbackQueryHandler(callback=mentors_end, pattern='mentors_end'), group=0)
dp.add_handler(CallbackQueryHandler(callback=return_to_mentors_list, pattern='mentors_list_end'), group=0)
