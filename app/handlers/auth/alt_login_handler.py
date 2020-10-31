from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
import datetime
import pytz

from app import dp
from app.db.db import Session
from app.db.models import User
from app.handlers.auth.permissions import get_user_info
from app.handlers.schedule.notifications import schedule_notifications_job
from app.handlers.schedule.shedule_handler import NoEntriesException, WentWrongException, ChoicesException


ALT_LOGIN_ROLE, ALT_LOGIN_NAME, ALT_LOGIN_PATRONYMIC, ALT_LOGIN_SURNAME, ALT_LOGIN_GROUP, ALT_LOGIN_POST, \
 ALT_LOGIN_DIRECTIONS = range(7)

alt_login_replicas = {
    'start': '<b>Алтернативная авторизация в чат-боте проектного офиса ИКТИБ</b>\n\nВы студент или наставник?',
    'stop': 'Альтернативная авторизация прервана.',
    'already': 'Вы уже авторизованы',
    'not_get_it': 'Прошу прощения, но я вас не до конца понял. Можете ответить на этот вопрос еще раз?',
    'name': 'Введите ваше настоящее имя',
    'patronymic': 'Введите ваше отчество',
    'surname': 'Введите вашу фамилию',
    'group': 'Введите учебную группу, в которой вы обучаетесь на данный момент',
    'post': 'Введите вашу должность',
    'gone_wrong': 'Что-то пошло не так, начните заново с ввода команды. Извините :(',
    'directions': 'Введите ваши направления работы и деятельности',
    'notification_error': 'Пока я пытался установить уведомления на ваш аккаунт произошла ошибка. ' +
                          'Возможно расписание недоступно или в профиле указана неверная группа. Попробуйте позже',
    'complete': 'Теперь вы пользователь чат-бота проектного офиса ИКТИБ. Проверить это вы можете через команду /profile'
}


def alt_login_start(update, context):
    user = get_user_info(update)
    if user:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=alt_login_replicas['already']
        )
        return ConversationHandler.END
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=alt_login_replicas['start']
        )
        return ALT_LOGIN_ROLE


def alt_login_role(update, context):
    user_message = update.message.text.lower()
    if 'студент' in user_message:
        context.user_data['role'] = 'student'
    elif 'наставник' in user_message:
        context.user_data['role'] = 'mentor'
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=alt_login_replicas['not_get_it']
        )
        return ALT_LOGIN_ROLE
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=alt_login_replicas['name']
    )
    return ALT_LOGIN_NAME


def alt_login_name(update, context):
    user_name = update.message.text
    context.user_data['name'] = user_name

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=alt_login_replicas['patronymic']
    )
    return ALT_LOGIN_PATRONYMIC


def alt_login_patronymic(update, context):
    user_name = update.message.text
    context.user_data['patronymic'] = user_name

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=alt_login_replicas['surname']
    )
    return ALT_LOGIN_SURNAME


def alt_login_surname(update, context):
    user_name = update.message.text
    context.user_data['surname'] = user_name

    role = context.user_data['role']
    if role == 'student':
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=alt_login_replicas['group']
        )
        return ALT_LOGIN_GROUP
    elif role == 'mentor':
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=alt_login_replicas['post']
        )
        return ALT_LOGIN_POST
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=alt_login_replicas['gone_wrong']
        )
        return ConversationHandler.END


def alt_login_group(update, context):
    group = update.message.text
    context.user_data['group'] = group

    user = complete_alt_login(update, context)

    if user:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=alt_login_replicas['complete']
        )
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=alt_login_replicas['gone_wrong']
        )
    return ConversationHandler.END


def alt_login_post(update, context):
    post = update.message.text
    context.user_data['post'] = post

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=alt_login_replicas['directions']
    )
    return ALT_LOGIN_DIRECTIONS


def alt_login_directions(update, context):
    directions = update.message.text
    context.user_data['directions'] = directions

    user = complete_alt_login(update, context)

    if user:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=alt_login_replicas['complete']
        )
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=alt_login_replicas['gone_wrong']
        )
    return ConversationHandler.END


def complete_alt_login(update, context):
    session = Session()
    role = context.user_data.get('role', '-')

    name = context.user_data.get('name', '-')
    patronymic = context.user_data.get('patronymic', '-')
    surname = context.user_data.get('surname', '-')

    group = '-'
    post = '-'
    directions = '-'
    if role == 'student':
        group = context.user_data.get('group', '-')

    elif role == 'mentor':
        post = context.user_data.get('post', '-')
        directions = context.user_data.get('directions', '-')

    user = User(
        tg_chat_id=update.message.chat_id,
        role=role,
        name=name,
        surname=surname,
        patronymic=patronymic,
        group=group,
        post=post,
        directions=directions
    )

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
            text=alt_login_replicas['notification_error']
        )

    session.add(user)
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f"Здравствуйте, {user.name} {user.patronymic}. Вы авторизованы."
    )

    context.user_data.pop('role', None)
    context.user_data.pop('name', None)
    context.user_data.pop('patronymic', None)
    context.user_data.pop('surname', None)
    context.user_data.pop('group', None)
    context.user_data.pop('post', None)
    context.user_data.pop('directions', None)

    session.commit()
    session.close()

    return user


def stop_alt_login(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=alt_login_replicas['stop']
    )
    return ConversationHandler.END


dp.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler(command='altlogin', callback=alt_login_start)],
        states={
            ALT_LOGIN_ROLE: [MessageHandler(filters=Filters.text, callback=alt_login_role)],
            ALT_LOGIN_NAME: [MessageHandler(filters=Filters.text, callback=alt_login_name)],
            ALT_LOGIN_PATRONYMIC: [MessageHandler(filters=Filters.text, callback=alt_login_patronymic)],
            ALT_LOGIN_SURNAME: [MessageHandler(filters=Filters.text, callback=alt_login_surname)],
            ALT_LOGIN_GROUP: [MessageHandler(filters=Filters.text, callback=alt_login_group)],
            ALT_LOGIN_POST: [MessageHandler(filters=Filters.text, callback=alt_login_post)],
            ALT_LOGIN_DIRECTIONS: [MessageHandler(filters=Filters.text, callback=alt_login_directions)]
        },
        fallbacks=[]
    )
)
