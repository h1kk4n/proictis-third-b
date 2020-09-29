from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters

from app import dp


REG_ROLE, REG_NAME, REG_PATRONYMIC, REG_SURNAME, REG_GROUP, REG_POST, REG_DIRECTIONS, \
 REG_EMAIL, REG_PHONE, REG_PASS = range(10)


def register_start(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='<b>Регистрация на сайте Проектного офиса ИКТИБ</b>\n\nВы студент или наставник?'
    )
    return REG_ROLE


def register_role(update, context):
    user_message = update.message.text.lower()
    if 'студент' in user_message:
        context.user_data['role'] = 'student'
    elif 'наставник' in user_message:
        context.user_data['role'] = 'mentor'
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Прошу прощения, но я вас не до конца понял. Можете ответить на этот вопрос еще раз?'
        )
        return REG_ROLE
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Введите ваше настоящее имя'
    )
    return REG_NAME


def register_name(update, context):
    user_name = update.message.text
    context.user_data['name'] = user_name

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Введите ваше отчество'
    )
    return REG_PATRONYMIC


def register_patronymic(update, context):
    user_name = update.message.text
    context.user_data['patronymic'] = user_name

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Введите вашу фамилию'
    )
    return REG_SURNAME


def register_surname(update, context):
    user_name = update.message.text
    context.user_data['surname'] = user_name

    role = context.user_data['role']
    if role == 'student':
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите учебную группу, в которой вы обучаетесь на данный момент'
        )
        return REG_GROUP
    elif role == 'mentor':
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите вашу должность'
        )
        return REG_ROLE
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Что-то пошло не так, начните заново с ввода команды. Извините :('
        )
        return ConversationHandler.END


def register_group(update, context):
    group = update.message.text
    context.user_data['group'] = group

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Введите электронную почту, к которой вы хотели бы привязать аккаунт'
    )
    return REG_EMAIL


def register_post(update, context):
    post = update.message.text
    context.user_data['post'] = post

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Введите ваши направления работы и деятельности'
    )
    return REG_DIRECTIONS


def register_directions(update, context):
    directions = update.message.text
    context.user_data['directions'] = directions

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Введите электронную почту, к которой вы хотели бы привязать аккаунт'
    )
    return REG_EMAIL


def register_email(update, context):
    email = update.message.text
    if '@' in email and email[email.find('@') + 1:]:
        context.user_data['email'] = email
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите действительную электронную почту. Пример: email@example.com'
        )
        return REG_EMAIL

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Введите ваш номер телефона'
    )
    return REG_PHONE


def register_phone(update, context):
    phone = update.message.text

    if phone.startswith('+7') and len(phone) == 12 or phone.startswith('8') and len(phone) == 11:
        context.user_data['phone'] = phone
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Попробуйте еще раз. Корректный номер должен быть в форме +79991235566 или 89991235566'
        )
        return REG_PHONE

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Введите ваш пароль. Сообщение с ним будет удалено впоследствии, чтобы не оставлять его открытым в чате'
    )
    return REG_PASS


def register_pass(update, context):
    password = update.message.text

    context.bot.delete_message(
        chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='*сообщение с паролем удалено*'
    )

    if len(password) >= 8:
        context.user_data['password'] = password
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Пароль слишком короткий. Минимальная длина - 8 символов. Попробуйте еще раз'
        )
        return REG_PASS
    # ...


def complete_registration(context):
    role = context.user_data.get('role', None)

    name = context.user_data.get('name', None)
    patronymic = context.user_data.get('patronymic', None)
    surname = context.user_data.get('surname', None)
    email = context.user_data.get('email', None)
    phone = context.user_data.get('phone', None)
    password = context.user_data.get('password', None)

    user_data = {
        'email': email,
        'name': name,
        'password': password,
        'patronymic': patronymic,
        'phone': phone,
        'role': role,
        'surname': surname
    }

    if role == 'student':
        group = context.user_data.get('group', None)
        user_data['group'] = group

    elif role == 'mentor':
        post = context.user_data.get('post', None)
        directions = context.user_data.get('directions', None)

        user_data['post'] = post
        user_data['directions'] = directions

    # ...


def stop_register(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Регистрация прервана.'
    )
    return ConversationHandler.END


dp.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler(command='register', callback=register_start)],
        states={
            REG_ROLE: [MessageHandler(filters=Filters.text, callback=register_role)],
            REG_NAME: [MessageHandler(filters=Filters.text, callback=register_name)],
            REG_PATRONYMIC: [MessageHandler(filters=Filters.text, callback=register_patronymic)],
            REG_SURNAME: [MessageHandler(filters=Filters.text, callback=register_surname)],
            REG_GROUP: [MessageHandler(filters=Filters.text, callback=register_group)],
            REG_POST: [MessageHandler(filters=Filters.text, callback=register_post)],
            REG_DIRECTIONS: [MessageHandler(filters=Filters.text, callback=register_directions)],
            REG_EMAIL: [MessageHandler(filters=Filters.text, callback=register_email)],
            REG_PHONE: [MessageHandler(filters=Filters.text, callback=register_phone)],
            REG_PASS: [MessageHandler(filters=Filters.text, callback=register_pass)]
        },
        fallbacks=[]
    )
)
