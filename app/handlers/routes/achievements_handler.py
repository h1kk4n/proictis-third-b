import os.path
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler

import app.web_functions
from config import Config
from app import dp


achievements_file_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '.data_achievements.json')
achievements_url = Config.BASE_URL + Config.url_path['achievements']


def form_achievements_list():

    achievements_json = app.web_functions.get_json_info(achievements_file_dir, achievements_url)

    message = '<b>Достижения студентов:</b>\n\n'
    all_achievements = list(reversed(achievements_json))
    for i in range(5):
        message += f"-{all_achievements[i]['title']}\n {all_achievements[i]['shortDescription']}\n {'-' * 50}\n\n"
    message += f'\n<i>Источник</i>: {achievements_url}'
    return message


def form_achievements_keyboard(achievements_amount=None):

    achievements_json = app.web_functions.get_json_info(achievements_file_dir, achievements_url)

    if achievements_amount is None:
        achievements_amount = len(achievements_json)

    all_achievements = list(reversed(achievements_json))
    keyboard_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=f"{all_achievements[i]['title']}",
            callback_data=f"achievements: {all_achievements[i]['_id']}"
        )] for i in range(achievements_amount)
    ] + [[InlineKeyboardButton(text='Назад', callback_data='achievements_return')]])

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


def do_achievements(update, context):

    bot_message = form_achievements_list()

    keyboard_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Подробнее", callback_data='achievements_more'),
         InlineKeyboardButton(text='Показать все', callback_data='achievements_show_all')],
         [InlineKeyboardButton(text="Закончить", callback_data='achievements_end')]
    ])

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=bot_message,
        reply_markup=keyboard_markup
    )


def more_achievements(update, context):

    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    new_keyboard_markup = form_achievements_keyboard(5)

    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text='<b>Достижения студентов:</b>\n'
    )

    context.bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=new_keyboard_markup
    )


def show_all_achievements(update, context):

    keyboard_markup = form_achievements_keyboard()

    context.bot.edit_message_text(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        text='<b>Достижения студентов:</b>\n'
    )

    context.bot.edit_message_reply_markup(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=keyboard_markup
    )


def find_achievements(update, context):
    achievements_id = update.callback_query.data.replace('achievements: ', '')

    achievements_json = app.web_functions.get_json_info(achievements_file_dir, achievements_url)

    founded_achievements = None
    bot_message = None
    for achievements in achievements_json:
        if achievements['_id'] == achievements_id:
            founded_achievements = achievements
            bot_message = f"<b>{achievements['title']}</b>\n\n" \
                          f"{achievements['description']}\n"

    context.bot.delete_message(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id
    )

    keyboard_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Назад", callback_data='achievements_back'),
         InlineKeyboardButton(text='Показать все', callback_data='achievements_to_all')],
         [InlineKeyboardButton(text="Закончить", callback_data='achievements_end')]
    ])
    context.bot.send_photo(
        chat_id=update.callback_query.message.chat_id,
        photo=founded_achievements['images'][0]['link']
    )

    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text=bot_message,
        reply_markup=keyboard_markup
    )


def achievements_back(update, context):

    keyboard_markup = form_achievements_keyboard(5)

    delete_message_and_photo(update, context)

    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text='<b>Достижения студентов:</b>\n',
        reply_markup=keyboard_markup
    )


def achievements_back_to_all(update, context):

    keyboard_markup = form_achievements_keyboard()

    delete_message_and_photo(update, context)

    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text='<b>Достижения студентов:</b>\n',
        reply_markup=keyboard_markup
    )


def return_to_achievements_list(update, context):

    bot_message = form_achievements_list()

    keyboard_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Подробнее", callback_data='achievements_more'),
         InlineKeyboardButton(text='Показать все', callback_data='achievements_show_all')],
         [InlineKeyboardButton(text="Закончить", callback_data='achievements_end')]
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


def achievements_end(update, context):
    context.bot.edit_message_reply_markup(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=None
    )


dp.add_handler(CommandHandler(command='achieves', callback=do_achievements), group=3)
dp.add_handler(CallbackQueryHandler(callback=more_achievements, pattern='achievements_more'), group=3)
dp.add_handler(CallbackQueryHandler(callback=show_all_achievements, pattern='achievements_show_all'), group=3)
dp.add_handler(CallbackQueryHandler(callback=find_achievements, pattern=r'achievements: .+'), group=3)
dp.add_handler(CallbackQueryHandler(callback=achievements_back, pattern='achievements_back'), group=3)
dp.add_handler(CallbackQueryHandler(callback=achievements_back_to_all, pattern='achievements_to_all'), group=3)
dp.add_handler(CallbackQueryHandler(callback=return_to_achievements_list, pattern='achievements_return'), group=3)
dp.add_handler(CallbackQueryHandler(callback=achievements_end, pattern='achievements_end'), group=3)