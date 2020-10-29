import os.path
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler

import app.web_functions
from config import Config
from app import dp


contests_file_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '.data_contests.json')
contests_url = Config.BASE_URL + Config.url_path['competitions']


def form_contests_list():

    contests_json = app.web_functions.get_json_info(contests_file_dir, contests_url)

    message = '<b>Актуальные конкурсы:</b>\n\n'
    all_contests = list(reversed(contests_json))
    for i in range(5):
        message += f"-{all_contests[i]['title']}\n {all_contests[i]['deadline']}\n {'-' * 50}\n\n"
    message += f'\n<i>Источник</i>: {contests_url}'
    return message


def form_contests_keyboard(contests_amount=None):

    contests_json = app.web_functions.get_json_info(contests_file_dir, contests_url)

    if contests_amount is None:
        contests_amount = len(contests_json)

    all_contests = list(reversed(contests_json))
    keyboard_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=f"{all_contests[i]['title']}",
            callback_data=f"contests: {all_contests[i]['_id']}"
        )] for i in range(contests_amount)
    ] + [[InlineKeyboardButton(text='Назад', callback_data='contests_return')]])

    return keyboard_markup


def delete_message_and_photo(update, context):

    context.bot.delete_message(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id - 1
    )

    context.bot.delete_message(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id
    )


def do_contests(update, context):

    bot_message = form_contests_list()

    keyboard_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Подробнее", callback_data='contests_more'),
         InlineKeyboardButton(text='Показать все', callback_data='contests_show_all')]
    ])

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=bot_message,
        reply_markup=keyboard_markup
    )


def more_contests(update, context):

    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    new_keyboard_markup = form_contests_keyboard(5)

    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text='<b>Актуальные конкурсы:</b>\n'
    )

    context.bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=new_keyboard_markup
    )


def show_all_contests(update, context):

    keyboard_markup = form_contests_keyboard()

    context.bot.edit_message_text(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        text='<b>Актуальные конкурсы:</b>\n'
    )

    context.bot.edit_message_reply_markup(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=keyboard_markup
    )


def find_contests(update, context):
    contests_id = update.callback_query.data.replace('contests: ', '')

    contests_json = app.web_functions.get_json_info(contests_file_dir, contests_url)

    founded_contests = None
    bot_message = None
    for contests in contests_json:
        if contests['_id'] == contests_id:
            founded_contests = contests
            bot_message = f"<b>{contests['title']}</b>\n\n" \
                          f"{contests['description']}\n"

    context.bot.delete_message(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id
    )

    keyboard_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Назад", callback_data='contests_back'),
         InlineKeyboardButton(text='Показать все', callback_data='contests_to_all')]
    ])
    context.bot.send_photo(
        chat_id=update.callback_query.message.chat_id,
        photo=founded_contests['images'][0]['link']
    )

    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text=bot_message,
        reply_markup=keyboard_markup
    )


def contests_back(update, context):

    keyboard_markup = form_contests_keyboard(5)

    delete_message_and_photo(update, context)

    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text='<b>Актуальные конкурсы:</b>\n',
        reply_markup=keyboard_markup
    )


def contests_back_to_all(update, context):

    keyboard_markup = form_contests_keyboard()

    delete_message_and_photo(update, context)

    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text='<b>Актуальные конкурсы:</b>\n',
        reply_markup=keyboard_markup
    )


def return_to_contests_list(update, context):

    bot_message = form_contests_list()

    keyboard_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Подробнее", callback_data='contests_more'),
         InlineKeyboardButton(text='Показать все', callback_data='contests_show_all')]
    ])

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


dp.add_handler(CommandHandler(command='contests', callback=do_contests), group=2)
dp.add_handler(CallbackQueryHandler(callback=more_contests, pattern='contests_more'), group=2)
dp.add_handler(CallbackQueryHandler(callback=show_all_contests, pattern='contests_show_all'), group=2)
dp.add_handler(CallbackQueryHandler(callback=find_contests, pattern=r'contests: .+'), group=2)
dp.add_handler(CallbackQueryHandler(callback=contests_back, pattern='contests_back'), group=2)
dp.add_handler(CallbackQueryHandler(callback=contests_back_to_all, pattern='contests_to_all'), group=2)
dp.add_handler(CallbackQueryHandler(callback=return_to_contests_list, pattern='contests_return'), group=2)
