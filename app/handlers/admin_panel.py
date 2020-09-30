from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters

from app import dp
from app.db.db import fully_refill_projects_and_teams_database
from app.db.db import Session
from app.db.models import User
from config import Config

ADD_ADMIN, REMOVE_ADMIN = range(2)


# Checks user status
def is_owner(update):
    return Config.OWNER_TG_ID == update.message.chat_id


def check_admin_status(update, context):
    session = Session()

    user_stats = session.query(User).filter(User.tg_chat_id == update.message.chat_id).first()

    session.close()

    if user_stats:
        return user_stats.is_admin or is_owner(update)

    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='У вас нет таких прав. Вы не авторизованы'
        )


def not_enough_permission(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Вы не являетесь администратором, потому не имеете права использовать эту функцию'
    )


# Add mew admin
def add_admin_info(update, context):

    if check_admin_status(update, context):
        bot_message = 'Введите chat_id нового администратора в телеграме. Идентификатор часа можно получить ' \
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
    new_admin_id = update.message.text

    user = session.query(User).filter(User.tg_chat_id == new_admin_id).first()

    if user:
        user.is_admin = True
        session.commit()
        session.close()

        bot_message = f"{user.surname} {user.name} теперь администратор чат-бота проектного офиса ИКТИБ"

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=bot_message
        )

    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Такого пользователя нет в нашей базе. Попросите этого человека авторизоваться через /login'
        )

    return ConversationHandler.END


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
    new_admin_id = update.message.text

    user = session.query(User).filter(User.tg_chat_id == new_admin_id).first()

    if user:
        if user.is_admin:
            user.is_admin = False
            session.commit()
            session.close()

            bot_message = f"{user.surname} {user.name} больше не администратор чат-бота"

            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=bot_message
            )

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


dp.add_handler(CommandHandler(command='dbrefill', callback=admin_db_refill))
dp.add_handler(ConversationHandler(
    entry_points=[
        CommandHandler(command='newadmin', callback=add_admin_info),
        CommandHandler(command='deladmin', callback=remove_admin_info)
    ],
    states={
        ADD_ADMIN: [MessageHandler(filters=Filters.text, callback=add_admin)],
        REMOVE_ADMIN: [MessageHandler(filters=Filters.text, callback=remove_admin)]
    },
    fallbacks=[]
))