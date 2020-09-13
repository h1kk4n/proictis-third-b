import json
import gspread

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from oauth2client.service_account import ServiceAccountCredentials

from models import Base
from models import FirstProject, SecondProject, Team

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
                    members.append(member)

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


def fully_refill_database():
    recreate_database()
    fill_projects('1bzRdpJMghpo0fvUtd5CInKh96tdSikiAdg9fnK3nLLs', FirstProject)
    fill_teams('1bzRdpJMghpo0fvUtd5CInKh96tdSikiAdg9fnK3nLLs')

    fill_projects('1aPFMDFrQWk6tJn-EMHUTI-CpBNYN2n92jSuf8VHPgOg', SecondProject)
    fill_teams('1aPFMDFrQWk6tJn-EMHUTI-CpBNYN2n92jSuf8VHPgOg')


if __name__ == '__main__':

    # print(Base.metadata.tables['teams'].create(bind=engine))

    fully_refill_database()
