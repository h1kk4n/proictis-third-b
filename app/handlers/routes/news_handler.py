import os.path
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler

from pprint import pprint

import app.web_functions
from config import Config
from app import dp


news_file_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '.data_news.json')
news_url = Config.BASE_URL + Config.url_path['news']


def form_news_list():

    news_json = app.web_functions.get_json_info(news_file_dir, news_url)

    message = '<b>Актуальные новости:</b>\n\n'
    all_news = list(reversed(news_json))
    for i in range(5):
        message += f"-{all_news[i]['title']}\n {all_news[i]['shortDescription']}\n {'-' * 50}\n\n"
    message += f'\n<i>Источник</i>: {news_url}'
    return message


def form_news_keyboard(news_amount=None):

    news_json = app.web_functions.get_json_info(news_file_dir, news_url)

    if news_amount is None:
        news_amount = len(news_json)

    all_news = list(reversed(news_json))
    keyboard_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=f"{all_news[i]['title']}",
            callback_data=f"news: {all_news[i]['_id']}"
        )] for i in range(news_amount)
    ] + [[InlineKeyboardButton(text='Назад', callback_data='news_return')]])

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


def do_news(update, context):

    bot_message = form_news_list()

    keyboard_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Подробнее", callback_data='news_more'),
         InlineKeyboardButton(text='Показать все', callback_data='news_show_all')],
         [InlineKeyboardButton(text="Закончить", callback_data='news_end')]
    ])

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=bot_message,
        reply_markup=keyboard_markup
    )


def more_news(update, context):

    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    new_keyboard_markup = form_news_keyboard(5)

    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text='<b>Актуальные новости:</b>\n'
    )

    context.bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=new_keyboard_markup
    )


def show_all_news(update, context):

    keyboard_markup = form_news_keyboard()

    context.bot.edit_message_text(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        text='<b>Актуальные новости:</b>\n'
    )

    context.bot.edit_message_reply_markup(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=keyboard_markup
    )


def find_news(update, context):
    news_id = update.callback_query.data.replace('news: ', '')

    news_json = app.web_functions.get_json_info(news_file_dir, news_url)

    founded_news = None
    bot_message = None
    for news in news_json:
        if news['_id'] == news_id:
            founded_news = news
            bot_message = f"<b>{news['title']}</b>\n\n" \
                          f"{news['description']}\n"

    context.bot.delete_message(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id
    )

    keyboard_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Назад", callback_data='news_back'),
         InlineKeyboardButton(text='Показать все', callback_data='news_to_all')],
         [InlineKeyboardButton(text="Закончить", callback_data='news_end')]
    ])
    context.bot.send_photo(
        chat_id=update.callback_query.message.chat_id,
        photo=founded_news['images'][0]['link']
    )

    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text=bot_message,
        reply_markup=keyboard_markup
    )


def news_back(update, context):

    keyboard_markup = form_news_keyboard(5)

    delete_message_and_photo(update, context)

    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text='<b>Актуальные новости:</b>\n',
        reply_markup=keyboard_markup
    )


def news_back_to_all(update, context):

    keyboard_markup = form_news_keyboard()

    delete_message_and_photo(update, context)

    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text='<b>Актуальные новости:</b>\n',
        reply_markup=keyboard_markup
    )


def return_to_news_list(update, context):

    bot_message = form_news_list()

    keyboard_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Подробнее", callback_data='news_more'),
         InlineKeyboardButton(text='Показать все', callback_data='news_show_all')],
         [InlineKeyboardButton(text="Закончить", callback_data='news_end')]
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


def news_end(update, context):
    context.bot.edit_message_reply_markup(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=None
    )


dp.add_handler(CommandHandler(command='news', callback=do_news), group=1)
dp.add_handler(CallbackQueryHandler(callback=more_news, pattern='news_more'), group=1)
dp.add_handler(CallbackQueryHandler(callback=show_all_news, pattern='news_show_all'), group=1)
dp.add_handler(CallbackQueryHandler(callback=find_news, pattern=r'news: .+'), group=1)
dp.add_handler(CallbackQueryHandler(callback=news_back, pattern='news_back'), group=1)
dp.add_handler(CallbackQueryHandler(callback=news_back_to_all, pattern='news_to_all'), group=1)
dp.add_handler(CallbackQueryHandler(callback=return_to_news_list, pattern='news_return'), group=1)
dp.add_handler(CallbackQueryHandler(callback=news_end, pattern='news_end'), group=1)