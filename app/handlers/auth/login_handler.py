from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
import requests
import datetime
import pytz

from app import dp
from app.db.models import User
from app.db.db import Session
from app.handlers.schedule.notifications import schedule_notifications_job
from app.handlers.schedule.shedule_handler import NoEntriesException, ChoicesException, WentWrongException
from config import Config


LOGIN_EMAIL, LOGIN_PASSWORD, LOGIN_END = range(3)
LOGIN_URL = Config.BASE_URL + Config.url_path['login']

auth_replicas = {
    'too_much_args': 'Передано больше двух аргументов. Сообщение удалено, т.к. оно могло содержать пароль\n\n' +
                     'Используя команду /login, вводите только электронную почту и пароль.',
    'enter_email': 'Введите вашу электронную почту',
    'enter_pass': 'Введите пароль',
    'delete_pass': '* сообщение с паролем удалено *',
    'something_gone_wrong': 'Что-то пошло не так в последнюю секунду',
    'not_activated_account': 'Вы не активировали свой аккаунт Проектного Офиса ИКТИБ',
    'notification_error': 'Пока я пытался установить уведомления на ваш аккаунт произошла ошибка. ' +
                          'Возможно расписание недоступно или в профиле указана неверная группа. Попробуйте позже',
    'logout': 'Вы вышли из сети. Теперь вы для нас загадка',
    'not_logged': 'Вы не авторизованы'
}


def do_login_email(update, context):
    context.user_data['email'] = update.message.text

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=auth_replicas['enter_pass']
    )
    return LOGIN_PASSWORD


def do_login_auth(update, context):
    login_data = {
        'email': context.user_data['email'],
        'password': context.user_data['password']
    }

    login_result = requests.post(
        url=LOGIN_URL,
        data=login_data
    ).json()

    if login_result['auth']:
        session = Session()
        user_info = login_result['user']

        if user_info['role'] == 'student':
            user = User(
                tg_chat_id=update.message.chat_id,
                role=user_info['role'],
                surname=user_info['surname'],
                name=user_info['name'],
                patronymic=user_info['patronymic'],
                group=user_info['group'],
                email=user_info['email'],
                phone=user_info['phone'],
                post='',
                directions='',
                is_notified=True,
                is_admin=False
            )

        elif user_info['role'] == 'mentor':
            user = User(
                tg_chat_id=update.message.chat_id,
                role=user_info['role'],
                surname=user_info['surname'],
                name=user_info['name'],
                patronymic=user_info['patronymic'],
                group='',
                email=user_info['email'],
                phone=user_info['phone'],
                post=user_info['post'],
                directions=user_info['directions']
            )

        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=auth_replicas['something_gone_wrong']
            )
            return ConversationHandler.END

        try:
            schedule_notifications_job(context, user)
            context.job_queue.run_daily(
                schedule_notifications_job,
                time=datetime.time(hour=1, minute=0, tzinfo=pytz.timezone('Etc/GMT-3')),
                days=(0, 1, 2, 3, 4, 5),
                context=user,
                name='Обновить расписание'
            )
            user.is_notified = True
        except (NoEntriesException, WentWrongException, ChoicesException):
            context.bot.send_message(
                chat_id=user.tg_chat_id,
                text=auth_replicas['notification_error']
            )

        session.add(user)
        session.commit()

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"Здравствуйте, { user.name } { user.patronymic }. Вы авторизованы."
        )

        session.close()

    else:

        if 'message' in context.user_data.keys():
            if 'message' == "User didn't activated account.":
                context.bot.sendMessage(
                    chat_id=update.message.chat_id,
                    text=auth_replicas['not_activated_account']
                )

        else:
            context.bot.sendMessage(
                chat_id=update.message.chat_id,
                text=auth_replicas['something_gone_wrong']
            )

    del context.user_data['email']
    del context.user_data['password']

    return ConversationHandler.END


def do_login_password(update, context):
    context.user_data['password'] = update.message.text

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=auth_replicas['delete_pass']
    )

    return do_login_auth(update, context)


def do_login(update, context):
    try:
        session = Session()
        user = session.query(User).filter(User.tg_chat_id == update.message.chat_id).first()

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"Вы уже авторизованы, {user.name} {user.patronymic}"
        )
        session.close()

    except:
        if len(context.args) > 2:
            context.bot.delete_message(
                chat_id=update.message.chat_id,
                message_id=update.message.message_id
            )

            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=auth_replicas['too_much_args']
            )

            return ConversationHandler.END

        elif len(context.args) >= 1:
            context.user_data['email'] = context.args[0]

            if len(context.args) == 2:
                context.user_data['password'] = context.args[1]

                context.bot.delete_message(
                    chat_id=update.message.chat_id,
                    message_id=update.message.message_id
                )

                return do_login_auth(update, context)

            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=auth_replicas['enter_pass']
            )
            return LOGIN_PASSWORD

        else:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=auth_replicas['enter_email']
            )
            return LOGIN_EMAIL


def do_logout(update, context):
    session = Session()

    user = session.query(User).filter(User.tg_chat_id == update.message.chat_id).first()

    if user:
        session.delete(user)
        session.commit()

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=auth_replicas['logout']
        )

    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=auth_replicas['not_logged']
        )

    session.close()


dp.add_handler(
    ConversationHandler(
        entry_points=[
            CommandHandler(command='login', callback=do_login, pass_args=True, pass_job_queue=True)
        ],
        states={
            LOGIN_EMAIL: [MessageHandler(filters=Filters.text, callback=do_login_email, pass_job_queue=True)],
            LOGIN_PASSWORD: [MessageHandler(filters=Filters.text, callback=do_login_password, pass_job_queue=True)]
        },
        fallbacks=[]
    )
)
dp.add_handler(CommandHandler(command='logout', callback=do_logout))
