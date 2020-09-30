from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean


Base = declarative_base()


class FirstProject(Base):
    __tablename__ = 'first_project'
    id = Column(Integer, primary_key=True)
    mentor = Column(String)
    name = Column(String)
    additional_info = Column(String)
    description = Column(String)
    team_1 = Column(String)
    team_2 = Column(String)
    team_3 = Column(String)

    def __repr__(self):
        return f"<b><i>{ self.name }</i></b>\n\n" \
               f"<b>Наставник</b>: { self.mentor }\n\n" \
               f"<b>Команды</b>:\n" \
               f"-{ self.team_1 or 'x' }\n" \
               f"-{ self.team_2 or 'x' }\n" \
               f"-{ self.team_3 or 'x' }"


class SecondProject(Base):
    __tablename__ = 'second_project'
    id = Column(Integer, primary_key=True)
    mentor = Column(String)
    name = Column(String)
    additional_info = Column(String)
    description = Column(String)
    team_1 = Column(String)
    team_2 = Column(String)
    team_3 = Column(String)

    def __repr__(self):
        return f"{self.name}\n\n" \
               f"<b>Наставник</b>: {self.mentor}\n\n" \
               f"<b>Команды</b>:\n" \
               f"-{self.team_1 or 'x'}\n" \
               f"-{self.team_2 or 'x'}\n" \
               f"-{self.team_3 or 'x'}"


class Team(Base):
    __tablename__ = 'teams'
    name = Column(String, primary_key=True)
    member_1 = Column(String)
    member_2 = Column(String)
    member_3 = Column(String)
    member_4 = Column(String)
    member_5 = Column(String)
    member_6 = Column(String)
    member_7 = Column(String)
    member_8 = Column(String)

    def __repr__(self):
        return f"Команда <b><i>{ self.name }</i></b>\n\n" \
               f"<b>Участники</b>:\n" \
               f"-{ self.member_1 or 'x' }\n" \
               f"-{ self.member_2 or 'x' }\n" \
               f"-{ self.member_3 or 'x' }\n" \
               f"-{ self.member_4 or 'x' }\n" \
               f"-{ self.member_5 or 'x' }\n" \
               f"-{ self.member_6 or 'x' }\n" \
               f"-{ self.member_7 or 'x' }\n" \
               f"-{ self.member_8 or 'x' }"


class User(Base):
    __tablename__ = 'users'
    tg_chat_id = Column(Integer, primary_key=True)
    role = Column(String)
    surname = Column(String)
    name = Column(String)
    patronymic = Column(String)
    group = Column(String)
    post = Column(String)
    directions = Column(String)
    email = Column(String)
    phone = Column(String)
    is_admin = Column(Boolean)

    def __repr__(self):
        if self.role == 'student':
            return f"Вы <b><i>{self.surname} {self.name} {self.patronymic}</i></b>\n\n" \
                   f"<u>Роль</u>: студент\n" \
                   f"<u>Группа</u>: {self.group}\n" \
                   f"<u>Почта</u>: {self.email}\n" \
                   f"<u>Телефон</u>: {self.phone}"
        if self.role == 'mentor':
            return f"Вы <b><i>{self.surname} {self.name} {self.patronymic}</i><b/>\n\n" \
                   f"<u>Роль</u>: наставник\n" \
                   f"<u>Должность</u>: {self.post}\n" \
                   f"<u>Направления</u>: {self.directions}\n" \
                   f"<u>Почта</u>: {self.email}\n" \
                   f"<u>Телефон</u>: {self.phone}"
