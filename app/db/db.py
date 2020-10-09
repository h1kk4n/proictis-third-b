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


def recreate_teams_and_projects_db():
    Base.metadata.tables['teams'].drop(bind=engine)
    Base.metadata.tables['teams'].create(bind=engine)
    Base.metadata.tables['first_project'].drop(bind=engine)
    Base.metadata.tables['first_project'].create(bind=engine)
    Base.metadata.tables['second_project'].drop(bind=engine)
    Base.metadata.tables['second_project'].create(bind=engine)


def drop_users_table():
    Base.metadata.tables['users'].drop(bind=engine)
    Base.metadata.tables['users'].create(bind=engine)
    return "Успешно"


def fill_projects_and_teams_from_spreadsheet(project_id, table_class):
    session = Session()

    worksheet = service.open_by_key(project_id).worksheet('Сводная таблица')

    values = worksheet.get_all_values()

    # useless
    del values[0]
    # name isn't necessary
    del values[0]

    teams_id = session.query(Team).count()
    for col in range(1, len(values[0])):

        mentor = values[0][col]
        additional_info = values[3][col].strip()
        if not mentor:
            i = col
            while not mentor and i > 0:
                mentor = worksheet.cell(3, i).value.strip().replace('\n', ' ')
                additional_info = worksheet.cell(6, i).value.strip().replace('\n', ' ')
                i -= 1

        project_name = values[2][col].strip().replace('\n', ' ')

        description = values[4][col].strip()

        team_1 = values[5][col].strip()
        team_2 = values[14][col].strip()
        team_3 = values[23][col].strip()

        project = table_class(
            id=col,
            mentor=mentor,
            name=project_name,
            description=description,
            additional_info=additional_info,
            team_1=team_1,
            team_2=team_2,
            team_3=team_3
        )

        session.add(project)

        for i in 5, 14, 23:

            team_name = values[i][col]
            if team_name:
                members = []
                for j in range(1, 9):
                    member = values[i + j][col]
                    if member.strip().lower() != 'x' and member.strip().lower() != 'х' and member.strip().lower():
                        members.append(member)
                    else:
                        members.append(None)

                team = Team(
                    id=teams_id,
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
                teams_id += 1

                session.add(team)

    session.commit()

    session.close()


def fill_teams_and_projects(projects_list, project_table_class):
    session = Session()

    project_id = session.query(project_table_class).count()
    teams_id = session.query(Team).count()

    for i in range(len(projects_list)):
        print(i)
        mentor = projects_list[i]
        mentor_name = mentor['name'].strip().replace('\n', ' ')
        additional_info = mentor['contacts'].strip().replace('\n', ' ')
        for k in range(len(mentor['themes'])):
            theme = mentor['themes'][k].replace('\n', ' ').strip()
            project_name = theme['name'].strip().replace('\n', ' ')
            case = theme['documentLink'].strip().replace('\n', ' ') or None
            teams = [
                theme['teams'][0]['name'].strip().replace('\n', ' ') or None,
                theme['teams'][1]['name'].strip().replace('\n', ' ') or None,
                theme['teams'][2]['name'].strip().replace('\n', ' ') or None
            ]

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

            for j in range(len(teams)):
                if teams[j]:
                    members = theme['teams'][j]['members']
                    team = Team(
                        id=teams_id,
                        name=teams[j],
                        member_1=members[0].strip(),
                        member_2=members[1].strip(),
                        member_3=members[2].strip(),
                        member_4=members[3].strip(),
                        member_5=members[4].strip(),
                        member_6=members[5].strip(),
                        member_7=members[6].strip(),
                        member_8=members[7].strip()
                    )
                    session.add(team)

                    teams_id += 1

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
        # try:
            projects_info = requests.get(Config.BASE_URL + Config.url_path['projects']).json()

            first_project_id = projects_info[0]['link'].split('/')[-2]
            second_project_id = projects_info[1]['link'].split('/')[-2]

            fill_projects_and_teams_from_spreadsheet(first_project_id, FirstProject)
            fill_projects_and_teams_from_spreadsheet(second_project_id, SecondProject)
            return "Дело сделано, но не так, как планировалось"

        # except:
        #     return "Что-то пошло не так"

    else:

        fill_teams_and_projects(first_project, FirstProject)
        fill_teams_and_projects(second_project, SecondProject)
        return "Дело сделано"


def fully_refill_projects_and_teams_database():
    recreate_teams_and_projects_db()
    return make_teams_and_projects()


if __name__ == '__main__':

    # print(fully_refill_projects_and_teams_database())
    print(drop_users_table())
