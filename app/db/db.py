import json
import requests
import gspread

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from oauth2client.service_account import ServiceAccountCredentials

from app.db.models import Base
from app.db.models import FirstProject, SecondProject, Team

from config import Config

scopes = ['https://spreadsheets.google.com/feeds']

creds_dict = json.loads(Config.GOOGLE_SERVICE_ACCOUNT)
creds_dict["private_key"] = creds_dict["private_key"].replace("\\\\n", "\n")
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)
service = gspread.authorize(creds)

engine = create_engine(Config.DATABASE_URL)
Session = sessionmaker(bind=engine)


def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def fill_projects(project_id, table_class):
    session = Session()

    worksheet = service.open_by_key(project_id).worksheet('Сводная таблица')

    values = worksheet.get_all_values()

    # useless
    del values[0]
    # name isn't necessary
    del values[0]

    for col in range(1, len(values[0])):
        mentor = values[0][col]
        if not mentor:
            i = col
            while not mentor and i > 0:
                mentor = worksheet.cell(3, i).value
                i -= 1

        case = values[1][col].strip()
        project_name = values[2][col].strip()

        additional_info = values[4][col].strip()

        team_1 = values[5][col].strip()
        team_2 = values[14][col].strip()
        team_3 = values[23][col].strip()

        project = table_class(
            id=col,
            mentor=mentor,
            name=project_name,
            case=case,
            additional_info=additional_info,
            team_1=team_1,
            team_2=team_2,
            team_3=team_3
        )

        session.add(project)
    session.commit()

    session.close()


def fill_teams(project_id):
    session = Session()

    worksheet = service.open_by_key(project_id).worksheet('Сводная таблица')

    values = worksheet.get_all_values()

    # useless
    del values[0]
    # name isn't necessary
    del values[0]

    for col in range(1, len(values[0])):
        for i in 5, 14, 23:

            team_name = values[i][col]
            if team_name:
                members = []
                for j in range(1, 9):
                    member = values[i + j][col]
                    if member != 'x':
                        members.append(member)
                    else:
                        members.append(None)

                team = Team(
                    name=team_name,
                    member_1=members[0],
                    member_2=members[1],
                    member_3=members[2],
                    member_4=members[3],
                    member_5=members[4],
                    member_6=members[5],
                    member_7=members[6],
                    member_8=members[7]
                )

                session.add(team)
        session.commit()
        session.close()


def fill_teams_and_projects(projects_list, project_table_class):
    session = Session()

    for i in range(len(projects_list)):
        project_id = 0
        print(i)
        mentor = projects_list[i]
        mentor_name = mentor['name']
        additional_info = mentor['contacts']
        for k in range(len(mentor['themes'])):
            theme = mentor['themes'][k]
            project_name = theme['name']
            case = theme['documentLink'] or None
            teams = [
                theme['teams'][0]['name'] or None,
                theme['teams'][1]['name'] or None,
                theme['teams'][2]['name'] or None
            ]

            for j in range(len(teams)):
                if teams[j]:
                    members = theme['teams'][j]['members']
                    team = Team(
                        name=teams[j],
                        member_1=members[0],
                        member_2=members[1],
                        member_3=members[2],
                        member_4=members[3],
                        member_5=members[4],
                        member_6=members[5],
                        member_7=members[6],
                        member_8=members[7]
                    )
                    session.add(team)

            project = project_table_class(
                id=project_id,
                mentor=mentor_name,
                name=project_name,
                additional_info=additional_info,
                case=case,
                team_1=teams[0],
                team_2=teams[1],
                team_3=teams[2]
            )

            session.add(project)
            project_id += 1

    session.commit()
    session.close()


def make_teams_and_projects():
    try:
        projects_sheet = requests.get(Config.BASE_URL + Config.url_path['sheets']).json()
        projects_sheet.raise_for_status()

        first_project = projects_sheet[0]['structure']['mentors']
        second_project = projects_sheet[1]['structure']['mentors']

    except:
        try:
            projects_info = requests.get(Config.BASE_URL + Config.url_path['projects']).json()

            first_project_id = projects_info[0]['link'].split('/')[-2]
            second_project_id = projects_info[1]['link'].split('/')[-2]

            fill_projects(first_project_id, FirstProject)
            fill_projects(second_project_id, SecondProject)
            fill_teams(first_project_id)
            fill_teams(second_project_id)
            return "Дело сделано, но не так, как планировалось"

        except:
            return "Что-то пошло не так"

    else:

        fill_teams_and_projects(first_project, FirstProject)
        fill_teams_and_projects(second_project, SecondProject)
        return "Дело сделано"


def fully_refill_database():
    recreate_database()
    return make_teams_and_projects()


if __name__ == '__main__':

    # Base.metadata.tables['users'].drop(bind=engine)
    # Base.metadata.tables['users'].create(bind=engine)

    print(fully_refill_database())
