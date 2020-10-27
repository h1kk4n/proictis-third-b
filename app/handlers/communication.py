from telegram import InlineKeyboardButton

from app.handlers.projects.projects_handler import project_buttons
from app.handlers.auth.permissions import get_user_info
from app.db.models import User, Team, FirstProject, SecondProject
from app.db.db import Session


def add_write_all_teams_button(update, project, keyboard):
    user = get_user_info(update)
    if user.role == 'mentor' and project.mentor == f"{user.surname} {user.name} {user.patronymic}" and user.verified\
            or user.is_admin:
        keyboard.append(
            [InlineKeyboardButton(
                text='Написать всем командам',
                callback_data=project_buttons['write']['all_teams']
            )]
        )

    return keyboard


def add_write_team_button(update, project_number, team, keyboard):
    user = get_user_info(update)

    if user.role == 'mentor' and user.verified or user.is_admin:
        session = Session()
        mentor_projects = []
        if project_number == 'f':
            mentor_projects = session.query(FirstProject).filter(
                FirstProject.mentor == f"{user.surname} {user.name} {user.patronymic}"
            )
        elif project_number == 's':
            mentor_projects = session.query(SecondProject).filter(
                SecondProject.mentor == f"{user.surname} {user.name} {user.patronymic}"
            )

        for project in mentor_projects:
            if team.name in (project.team_1, project.team_2, project.team_3):
                keyboard.append(
                    [InlineKeyboardButton(
                        text='Написать команде',
                        callback_data=f"{project_buttons['write']['team']} {team.id}"
                    )]
                )
        session.close()

    return keyboard


def write_team(update, context):
    pass