from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters

from app import dp
from app.db.db import fully_refill_projects_and_teams_database, drop_users_table
from app.db.db import Session
from app.db.models import User
from app.handlers.auth.permissions import check_admin_status, not_enough_permission, is_owner

ADD_ADMIN, REMOVE_ADMIN, SEND_STUDENTS, SEND_MENTORS = range(4)


# Add mew admin
def add_admin_info(update, context):

    if check_admin_status(update, context):
        bot_message = 'Введите chat_id нового администратора в телеграме. Идентификатор чата можно получить ' \
                      'написав боту @userinfobot'
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=bot_message
        )

        return ADD_ADMIN

    else:
        not_enough_permission(update, context)
        return ConversationHandler.END


def add_admin(update, context):
    session = Session()
    try:
        new_admin_id = int(update.message.text)

        user = session.query(User).filter(User.tg_chat_id == new_admin_id).first()

        if user:
            user.is_admin = True
            bot_message = f"{user.surname} {user.name} теперь администратор чат-бота проектного офиса ИКТИБ"

            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=bot_message
            )

            session.commit()
            session.close()

        else:
            bot_message = 'Такого пользователя нет в нашей базе. Либо введенные данные неверны, либо этот пользователь'\
                          ' не авторизован. Во втором случае, попросите этого человека авторизоваться через /login'

            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=bot_message
            )

        return ConversationHandler.END

    except ValueError:
        bot_message = 'Пользовательский chat_id недействителен или неверен. Попробуйте ввести команду заново'

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=bot_message
        )


# Remove admin status
def remove_admin_info(update, context):

    if is_owner(update):
        bot_message = 'Введите chat_id действующего администратора чат-бота проектного офиса ИКТИБ. ' \
                      'Идентификатор часа можно получить написав боту @userinfobot'
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=bot_message
        )

        return REMOVE_ADMIN

    else:
        not_enough_permission(update, context)
        return ConversationHandler.END


def remove_admin(update, context):
    session = Session()
    new_admin_id = int(update.message.text)

    user = session.query(User).filter(User.tg_chat_id == new_admin_id).first()

    if user:
        if user.is_admin:
            user.is_admin = False

            bot_message = f"{user.surname} {user.name} больше не администратор чат-бота"

            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=bot_message
            )

            session.commit()
            session.close()

        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text='Этот пользователь и так не является администратором'
            )

    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Такого пользователя нет в нашей базе, он не может быть администратором'
        )
    return ConversationHandler.END


# Refill tables of first and second project also with teams
def admin_db_refill(update, context):

    if check_admin_status(update, context):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Подождите немного, мы пересобираем таблицы в базе данных'
        )

        bot_message = fully_refill_projects_and_teams_database()

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=bot_message
        )
    else:
        not_enough_permission(update, context)


# Drop users table
def do_drop_users_table(update, context):
    if check_admin_status(update,context):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Подождите немного, мы удаляем пользователей'
        )

        bot_message = drop_users_table()

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=bot_message
        )
    else:
        not_enough_permission(update, context)


# Send all
def send_students_start(update, context):
    if check_admin_status(update, context):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите сообщение, которое нужно передать всем студентам'
        )
        return SEND_STUDENTS
    else:
        not_enough_permission(update, context)
        return ConversationHandler.END


def send_students(update, context):
    session = Session()
    bot_message = update.message.text

    students = session.query(User).filter(User.role == 'student')
    admin = session.query(User).filter(User.tg_chat_id == update.message.chat_id).first()
    bot_message = f'{admin.name} {admin.surname} пишет:\n' \
                  f'"{bot_message}"'
    for student in students:
        context.bot.send_message(
            chat_id=student.tg_chat_id,
            text=bot_message
        )
    session.close()
    return ConversationHandler.END


dp.add_handler(CommandHandler(command='dbrefill', callback=admin_db_refill))
dp.add_handler(CommandHandler(command='dropusers', callback=do_drop_users_table))
dp.add_handler(ConversationHandler(
    entry_points=[
        CommandHandler(command='newadmin', callback=add_admin_info),
        CommandHandler(command='deladmin', callback=remove_admin_info),
        CommandHandler(command='notestudent', callback=send_students_start)
    ],
    states={
        ADD_ADMIN: [MessageHandler(filters=Filters.text, callback=add_admin)],
        REMOVE_ADMIN: [MessageHandler(filters=Filters.text, callback=remove_admin)],
        SEND_STUDENTS: [MessageHandler(filters=Filters.text, callback=send_students)]
    },
    fallbacks=[]
))