from telegram import InlineKeyboardButton
from telegram.ext import CallbackQueryHandler, MessageHandler, ConversationHandler
from telegram.ext import Filters

from app import dp
from app.handlers.auth.permissions import get_user_info, is_mentor
from app.db.models import User, Team, FirstProject, SecondProject
from app.db.db import Session

WRITE = range(1)

communication_buttons = {
    'write': {
        'all_teams': 'write_all_teams',
        'team': 'write_team'
    }
}


def add_write_all_teams_button(update, project, keyboard):
    user = get_user_info(update)
    if is_mentor(user=user) and project.mentor.strip() == f"{user.surname} {user.name} {user.patronymic}"\
            or user.is_admin:
        keyboard.append(
            [InlineKeyboardButton(
                text='Написать всем командам',
                callback_data=communication_buttons['write']['all_teams']
            )]
        )

    return keyboard


def add_write_team_button(update, project_number, team, keyboard):
    user = get_user_info(update)

    if is_mentor(user=user) or user.is_admin:
        session = Session()
        mentor_projects = []
        if project_number == 'fp':
            mentor_projects = session.query(FirstProject).filter(
                FirstProject.mentor == f"{user.surname} {user.name} {user.patronymic}"
            )
        elif project_number == 'sp':
            mentor_projects = session.query(SecondProject).filter(
                SecondProject.mentor == f"{user.surname} {user.name} {user.patronymic}"
            )

        for project in mentor_projects:
            if team.name in (project.team_1, project.team_2, project.team_3):
                keyboard.append(
                    [InlineKeyboardButton(
                        text='Написать команде',
                        callback_data=f"{communication_buttons['write']['team']} {team.id}"
                    )]
                )
        session.close()

    return keyboard


def write_team_ask_for_message(update, context):
    query = update.callback_query
    team_id = query.data.replace(communication_buttons['write']['team'], '').strip()
    context.user_data['team_id'] = team_id
    context.bot.send_message(
        chat_id=query.message.chat_id,
        text='Введите сообщение, которое хотите отослать студентам'
    )
    return WRITE


def write_team(update, context):
    session = Session()
    current_user = get_user_info(update)
    message = update.message.text
    message = f'{current_user.name} {current_user.patronymic} {current_user.surname} пишет всей вашей команде:\n' \
              f'"{message}"'
    team_ids = map(int, context.user_data['team_id'].split(';'))
    for team_id in team_ids:
        necessary_team = session.query(Team).filter(Team.id == team_id).first()
        members = [
            necessary_team.member_1,
            necessary_team.member_2,
            necessary_team.member_3,
            necessary_team.member_4,
            necessary_team.member_5,
            necessary_team.member_6,
            necessary_team.member_7,
            necessary_team.member_8
        ]
        for member in members:
            if member:
                member = member.replace(',', '').split()[:3]
                surname = member[0]
                name = members[1]
                patronymic = member[2]
                member_account = session.query(User).filter(
                    User.surname == surname and
                    User.name == name and
                    User.patronymic == patronymic
                ).first()
                if member_account is not None:
                    context.bot.send_message(
                        chat_id=member_account.tg_chat_id,
                        text=message
                    )
    session.close()
    return ConversationHandler.END


dp.add_handler(
    ConversationHandler(
        entry_points=[
            CallbackQueryHandler(pattern=communication_buttons['write']['team'], callback=write_team_ask_for_message)
        ],
        states={
            WRITE: [MessageHandler(filters=Filters.text, callback=write_team)]
        },
        fallbacks=[]
    )
)
