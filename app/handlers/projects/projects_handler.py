from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton

from app import dp
from app.db.db import Session
from app.db.models import FirstProject, SecondProject, Team


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


def make_project_info_with_keyboard(project_table_class, project_number):
    session = Session()

    reply_keyboard = []
    query_result = session.query(project_table_class).filter(project_table_class.id == project_number).first()

    bot_message = f"<b><i>{ query_result.name }</i></b>\n\n" \
                  f"<b>Наставник</b>: { query_result.mentor }\n\n" \
                  f"<b>Команды</b>:"

    if query_result.team_1:
        reply_keyboard.append(
            [InlineKeyboardButton(
                text=str(query_result.team_1),
                callback_data=f'first_project_team_info: {project_number} {str(query_result.team_1)}'
            )]
        )
    if query_result.team_2:
        reply_keyboard.append(
            [InlineKeyboardButton(
                text=str(query_result.team_2),
                callback_data=f'first_project_team_info: {project_number} {str(query_result.team_2)}'
            )]
        )
    if query_result.team_3:
        reply_keyboard.append(
            [InlineKeyboardButton(
                text=str(query_result.team_3),
                callback_data=f'first_project_team_info: {project_number} {str(query_result.team_3)}'
            )]
        )

    session.close()
    return bot_message, reply_keyboard


def make_project_themes_keyboard(project_table_class, callback_data):
    themes_list = get_project_themes(project_table_class)

    projects_keyboard = []

    left_col = range(0, len(themes_list), 2)
    right_col = range(1, len(themes_list), 2)

    grid = [(left_col[i], right_col[i]) for i in range(min(len(left_col), len(right_col)))]

    for i, j in grid:
        projects_keyboard.append(
            [InlineKeyboardButton(text=themes_list[i], callback_data=f"{callback_data}_info: {i + 1}"),
             InlineKeyboardButton(text=themes_list[j], callback_data=f"{callback_data}_info: {j + 1}")]
        )

    if left_col != right_col:
        project_num = len(themes_list)
        projects_keyboard.append(
            [InlineKeyboardButton(text=themes_list[-1], callback_data=f'{callback_data}_info: {project_num}')]
        )

    projects_keyboard.append(
        [InlineKeyboardButton(text='Назад', callback_data='choose_project_type'),
         InlineKeyboardButton(text='Закончить', callback_data=f'{callback_data}_themes_for_end')]
    )

    return InlineKeyboardMarkup(projects_keyboard)


def find_team_info(team_name):
    session = Session()

    query_result = str(session.query(Team).filter(Team.name == team_name).first())

    session.close()
    return query_result


def make_project_team_info_with_keyboard(request_data, callback_data):
    team_name = ' '.join(request_data.split()[1:])
    project_number = request_data.split()[0]

    team_info = find_team_info(team_name)

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text='Назад', callback_data=f'{callback_data}_info: {project_number}'),
          InlineKeyboardButton(text='Закончить', callback_data='project_end')]]
    )
    return team_info, keyboard


def projects_end(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    context.bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=None
    )


# Choosing kind of projects
def show_projects(update, context):
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text='Первый творческий проект', callback_data='show_first_project')],
         [InlineKeyboardButton(text='Второй творческий проект', callback_data='show_second_project')]]
    )

    query = update.callback_query

    if query is None:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Выберите категорию проектов:',
            reply_markup=reply_markup
        )
    else:
        context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text='Выберите категорию проектов:',
            reply_markup=reply_markup
        )


# First creative project
def first_projects_themes_buttons(update, context):
    projects_keyboard = make_project_themes_keyboard(FirstProject, 'first_project')

    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    bot_message = 'Темы первого творческого проекта:'

    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=bot_message,
        reply_markup=projects_keyboard
    )


def first_project_themes_for_end(update, context):
    query = update.callback_query

    themes_list = get_project_themes_list(FirstProject)

    bot_message = 'Темы первого творческого проекта:\n\n' + themes_list

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=bot_message,
        reply_markup=None
    )


def first_project_info(update, context):
    query = update.callback_query

    project_number = int(query.data.split()[1])

    bot_message, keyboard = make_project_info_with_keyboard(FirstProject, project_number)

    keyboard.append(
        [InlineKeyboardButton(text='Назад', callback_data='show_first_project'),
         InlineKeyboardButton(text='Закончить', callback_data=f'first_projects_end_info: {project_number}')]
    )

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=bot_message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def first_projects_end_info(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    project_number = int(query.data.replace('first_projects_end_info: ', ''))

    bot_message = make_project_info(FirstProject, project_number)

    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=bot_message,
        reply_markup=None
    )


def first_project_team_info(update, context):
    query = update.callback_query
    request_data = query.data.replace('first_project_team_info: ', '')

    team_info, keyboard = make_project_team_info_with_keyboard(request_data, 'first_project')

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=team_info,
        reply_markup=keyboard
    )


# Second creative project
def second_projects_themes_buttons(update, context):
    projects_keyboard = make_project_themes_keyboard(SecondProject, 'second_project')

    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id

    bot_message = 'Темы второго творческого проекта:'

    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=bot_message,
        reply_markup=projects_keyboard
    )


def second_project_themes_for_end(update, context):
    query = update.callback_query

    themes_list = get_project_themes_list(SecondProject)

    bot_message = 'Темы второго творческого проекта:\n\n' + themes_list

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=bot_message,
        reply_markup=None
    )


def second_project_info(update, context):
    query = update.callback_query

    project_number = int(query.data.split()[1])

    bot_message, keyboard = make_project_info_with_keyboard(SecondProject, project_number)

    keyboard.append(
        [InlineKeyboardButton(text='Назад', callback_data='show_second_project'),
         InlineKeyboardButton(text='Закончить', callback_data=f'second_projects_end_info: {project_number}')]
    )

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=bot_message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def second_projects_end_info(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    project_number = int(query.data.replace('second_projects_end_info: ', ''))

    bot_message = make_project_info(SecondProject, project_number)

    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=bot_message,
        reply_markup=None
    )


def second_project_team_info(update, context):
    query = update.callback_query

    request_data = query.data.replace('second_project_team_info: ', '')

    team_info, keyboard = make_project_team_info_with_keyboard(request_data, 'second_project')

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=team_info,
        reply_markup=keyboard
    )


dp.add_handler(CommandHandler(command='project', callback=show_projects))
dp.add_handler(CallbackQueryHandler(callback=show_projects, pattern='choose_project_type'))
# First creative project handlers
dp.add_handler(CallbackQueryHandler(callback=first_projects_themes_buttons, pattern='show_first_project'))
dp.add_handler(CallbackQueryHandler(callback=first_project_themes_for_end, pattern='first_project_themes_for_end'))
dp.add_handler(CallbackQueryHandler(callback=first_project_info, pattern='first_project_info'))
dp.add_handler(CallbackQueryHandler(callback=first_projects_end_info, pattern='first_projects_end_info'))
dp.add_handler(CallbackQueryHandler(callback=first_project_team_info, pattern='first_project_team_info'))
# Second creative project handlers
dp.add_handler(CallbackQueryHandler(callback=second_projects_themes_buttons, pattern='show_second_project'))
dp.add_handler(CallbackQueryHandler(callback=second_project_themes_for_end, pattern='second_project_themes_for_end'))
dp.add_handler(CallbackQueryHandler(callback=second_project_info, pattern='second_project_info'))
dp.add_handler(CallbackQueryHandler(callback=second_projects_end_info, pattern='second_projects_end_info'))
dp.add_handler(CallbackQueryHandler(callback=second_project_team_info, pattern='second_project_team_info'))

dp.add_handler(CallbackQueryHandler(callback=projects_end, pattern='project_end'))

if __name__ == '__main__':
    print(find_team_info('♂boys next door♂'))
