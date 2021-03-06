from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton

from app import dp
from app.db.db import Session
from app.db.models import FirstProject, SecondProject, Team, User
from app.handlers.projects.communication import add_write_team_button


project_buttons = {
    'choose': 'choose_project_type',
    'first': {
        'show': 'show_first_project',
        'themes_end': 'fp_themes_for_end',
        'info': 'fp_info',
        'team_info': 'fp_team_info'
    },
    'second': {
        'show': 'show_second_project',
        'themes_end': 'sp_themes_for_end',
        'info': 'sp_info',
        'team_info': 'sp_team_info'
    },
    'student': 'u',
    'end': 'project_end'
}


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

    bot_message = f"<b><i>{query_result.name}</i></b>\n\n" \
                  f"<b>Наставник</b>: {query_result.mentor}\n\n" \
                  f"Дополнительная информация: {query_result.additional_info  or '-'}\n" \
                  f"Описание проекта: <a href='{query_result.description or ''}'>ссылка на документ</a>"

    if query_result.team_1 or query_result.team_2 or query_result.team_3:
        bot_message += f"\n\n<b>Команды</b>:"
    if query_result.team_1:
        reply_keyboard.append(
            [InlineKeyboardButton(
                text=str(query_result.team_1),
                callback_data=f'{project_buttons["first"]["team_info"]}: {project_number} {str(query_result.team_1)}'
            )]
        )
    if query_result.team_2:
        reply_keyboard.append(
            [InlineKeyboardButton(
                text=str(query_result.team_2),
                callback_data=f'{project_buttons["first"]["team_info"]}: {project_number} {str(query_result.team_2)}'
            )]
        )
    if query_result.team_3:
        reply_keyboard.append(
            [InlineKeyboardButton(
                text=str(query_result.team_3),
                callback_data=f'{project_buttons["first"]["team_info"]}: {project_number} {str(query_result.team_3)}'
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
        [InlineKeyboardButton(text='Назад', callback_data=f'{project_buttons["choose"]}')]
    )

    return InlineKeyboardMarkup(projects_keyboard)


def find_team_info(team_name='', team_id=None):
    session = Session()

    if team_id is None:
        query_result = session.query(Team).filter(team_name == Team.name).first()
    else:
        query_result = session.query(Team).filter(team_id == Team.id).first()

    session.close()
    return query_result


def make_member_pattern(member):
    if member:
        member = member.replace(',', '').split()
        member = f"{member[0]} {member[1]}"
        return member
    else:
        return None


def make_project_team_info_with_keyboard(update, request_data, callback_data):
    founded_team = None
    try:
        team_id = int(request_data.split()[1])
        founded_team = find_team_info(team_id=team_id)
    except:
        team_name = ' '.join(request_data.split()[1:])
        founded_team = find_team_info(team_name=team_name)
    finally:
        project_number = request_data.split()[0]

        team_id = founded_team.id

        founded_members = [
            founded_team.member_1,
            founded_team.member_2,
            founded_team.member_3,
            founded_team.member_4,
            founded_team.member_5,
            founded_team.member_6,
            founded_team.member_7,
            founded_team.member_8,
        ]

        members = [
            make_member_pattern(founded_team.member_1),
            make_member_pattern(founded_team.member_2),
            make_member_pattern(founded_team.member_3),
            make_member_pattern(founded_team.member_4),
            make_member_pattern(founded_team.member_5),
            make_member_pattern(founded_team.member_6),
            make_member_pattern(founded_team.member_7),
            make_member_pattern(founded_team.member_8)
        ]

        keyboard = []

        for i in range(8):
            project = ''
            if callback_data == 'fp':
                project = 'f'
            elif callback_data == 'sp':
                project = 's'

            if members[i] is not None:
                keyboard.append(
                    [InlineKeyboardButton(
                        text=founded_members[i],
                        callback_data=f"{project_buttons['student']}: {members[i]} {team_id} {project} {project_number}"
                    )]
                )

        keyboard = add_write_team_button(update, callback_data, founded_team, keyboard)
        keyboard.append(
            [InlineKeyboardButton(text='Назад', callback_data=f'{callback_data}_info: {project_number}')]
        )
        return founded_team, InlineKeyboardMarkup(keyboard)


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
        [[InlineKeyboardButton(text='Первый творческий проект', callback_data=project_buttons["first"]["show"])],
         [InlineKeyboardButton(text='Второй творческий проект', callback_data=project_buttons["second"]["show"])]]
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
    projects_keyboard = make_project_themes_keyboard(FirstProject, 'fp')

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


def first_project_info(update, context):
    query = update.callback_query

    project_number = int(query.data.split()[1])

    bot_message, keyboard = make_project_info_with_keyboard(FirstProject, project_number)

    keyboard.append(
        [InlineKeyboardButton(text='Назад', callback_data=f'{project_buttons["first"]["show"]}')]
    )

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=bot_message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def first_project_team_info(update, context):
    query = update.callback_query
    request_data = query.data.replace(f'{project_buttons["first"]["team_info"]}: ', '')

    team, keyboard = make_project_team_info_with_keyboard(query, request_data, 'fp')

    bot_message = f"Команда <b><i>{ team.name }</i></b>\n\n" \
                  f"<b>Участники</b>:\n"

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=bot_message,
        reply_markup=keyboard
    )


# Second creative project
def second_projects_themes_buttons(update, context):
    projects_keyboard = make_project_themes_keyboard(SecondProject, 'sp')

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


def second_project_info(update, context):
    query = update.callback_query

    project_number = int(query.data.split()[1])

    bot_message, keyboard = make_project_info_with_keyboard(SecondProject, project_number)

    keyboard.append(
        [InlineKeyboardButton(text='Назад', callback_data=f'{project_buttons["second"]["show"]}')]
    )

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=bot_message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def second_project_team_info(update, context):
    query = update.callback_query

    request_data = query.data.replace(f'{project_buttons["second"]["team_info"]}: ', '')

    team, keyboard = make_project_team_info_with_keyboard(query, request_data, 'sp')

    bot_message = f"Команда <b><i>{team.name}</i></b>\n\n" \
                  f"<b>Участники</b>:\n"

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=bot_message,
        reply_markup=keyboard
    )


# Users usability
def show_student_info(update, context):
    session = Session()

    query = update.callback_query
    student = query.data.replace(f"{project_buttons['student']}: ", "").split()

    surname = student[0]
    name = student[1]

    team_id = int(student[2])
    project = student[-2]
    project_number = student[-1]

    user = session.query(User).filter(
        User.surname == surname,
        User.name == name,
        User.role == 'student'
    ).first()

    keyboard = []

    if project == 'f':
        keyboard.append(
            [InlineKeyboardButton(
                text='Назад',
                callback_data=f'{project_buttons["first"]["team_info"]}: {project_number} {team_id}'
            )]
        )
    elif project == 's':
        keyboard.append(
            [InlineKeyboardButton(
                text='Назад',
                callback_data=f'{project_buttons["first"]["team_info"]}: {project_number} {team_id}'
            )]
        )

    keyboard = InlineKeyboardMarkup(keyboard)

    if user:
        bot_message = f"<b><i>{user.surname} {user.name} {user.patronymic}</i></b>\n\n" \
                      f"<u>Роль</u>: студент\n" \
                      f"<u>Группа</u>: {user.group}\n" \
                      f"<u>Почта</u>: *конфиденциально*\n" \
                      f"<u>Телефон</u>: *конфиденциально*"
        context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=bot_message,
            reply_markup=keyboard
        )

    else:
        student = ' '.join(student[0:2])

        bot_message = f"Имя - <b>{student}</b>\n\n" \
                      f"У нас нет информации об этом студенте"

        context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=bot_message,
            reply_markup=keyboard
        )

    session.close()


dp.add_handler(CommandHandler(command='project', callback=show_projects))
dp.add_handler(CallbackQueryHandler(callback=show_projects, pattern=project_buttons["choose"]))

# First creative project handlers
dp.add_handler(CallbackQueryHandler(callback=first_projects_themes_buttons, pattern=project_buttons["first"]["show"]))
dp.add_handler(CallbackQueryHandler(callback=first_project_info, pattern=project_buttons["first"]["info"]))
dp.add_handler(CallbackQueryHandler(callback=first_project_team_info, pattern=project_buttons["first"]["team_info"]))

# Second creative project handlers
dp.add_handler(CallbackQueryHandler(callback=second_projects_themes_buttons, pattern=project_buttons["second"]["show"]))
dp.add_handler(CallbackQueryHandler(callback=second_project_info, pattern=project_buttons["second"]["info"]))
dp.add_handler(CallbackQueryHandler(callback=second_project_team_info, pattern=project_buttons["second"]["team_info"]))

# User Info
dp.add_handler(CallbackQueryHandler(callback=show_student_info, pattern=project_buttons['student']))
