from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton

from app import dp
from app.db.db import Session
from app.db.models import FirstProject, SecondProject


# General functions
def get_project_themes(project_table_class):
    session = Session()

    query_result = session.query(project_table_class.name).all()
    project_themes = [r.name for r in query_result]

    session.close()
    return project_themes


def get_project_themes_list(project_table_class):
    project_themes = get_project_themes(project_table_class)

    themes_list = ''
    for theme in project_themes:
        theme = theme.replace('\n', ' ')
        themes_list += f"-{ theme }\n"

    return themes_list


def make_project_info(project_table_class, project_number):
    session = Session()

    bot_message = str(session.query(project_table_class).filter(project_table_class.id == project_number).first())

    session.close()
    return bot_message


def projects_end(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    context.bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=None
    )


# Первый творческий проект
def first_project_themes(update, context):
    print(update.message.message_id)
    themes_list = get_project_themes_list(FirstProject)

    bot_message = 'Темы первого творческого проекта:\n\n' + themes_list

    keyboard_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text='Подробнее', callback_data='fprojects_more'),
          InlineKeyboardButton(text='Закончить', callback_data='projects_end')]]
    )

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=bot_message,
        reply_markup=keyboard_markup
    )


def first_projects_more(update, context):
    themes_list = get_project_themes(FirstProject)

    projects_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=theme, callback_data=f"fprojects: {number}")]
         for number, theme in enumerate(themes_list)] +
        [[InlineKeyboardButton(text='Назад', callback_data=f"fprojects_return")]]
    )

    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    bot_message = 'Темы первого творческого проекта:'

    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=bot_message
    )

    context.bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=projects_keyboard
    )


def first_projects_info(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    project_number = int(query.data.replace('fprojects: ', '')) + 1

    bot_message = make_project_info(FirstProject, project_number)

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text='Информация о командах', callback_data='fprojects_teams')],
         [InlineKeyboardButton(text='Назад', callback_data='fprojects_more'),
          InlineKeyboardButton(text='Закончить', callback_data='projects_end')]]
    )

    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=bot_message,
        reply_markup=keyboard
    )


def first_projects_return(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    themes_list = get_project_themes_list(FirstProject)

    bot_message = 'Темы первого творческого проекта:\n\n' + themes_list

    keyboard_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text='Подробнее', callback_data='fprojects_more'),
          InlineKeyboardButton(text='Закончить', callback_data='projects_end')]]
    )

    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=bot_message,
        reply_markup=keyboard_markup
    )


dp.add_handler(CommandHandler(command='fprojects', callback=first_project_themes))
dp.add_handler(CallbackQueryHandler(callback=first_projects_more, pattern='fprojects_more'))
dp.add_handler(CallbackQueryHandler(callback=first_projects_info, pattern=r'fprojects: \d+'))
dp.add_handler(CallbackQueryHandler(callback=first_projects_return, pattern='fprojects_return'))


# Второй творческий проект
def second_project_themes(update, context):
    themes_list = get_project_themes_list(SecondProject)

    bot_message = 'Темы второго творческого проекта:\n\n' + themes_list

    keyboard_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text='Подробнее', callback_data='sprojects_more'),
          InlineKeyboardButton(text='Закончить', callback_data='projects_end')]]
    )

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=bot_message,
        reply_markup=keyboard_markup
    )


def second_projects_more(update, context):
    pass


dp.add_handler(CommandHandler(command='sprojects', callback=second_project_themes))
dp.add_handler(CallbackQueryHandler(callback=second_projects_more, pattern='sprojects_more'))

dp.add_handler(CallbackQueryHandler(callback=projects_end, pattern='projects_end'))