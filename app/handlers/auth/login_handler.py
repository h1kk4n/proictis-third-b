from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
import requests

from pprint import pprint

from app import dp
from config import Config


LOGIN_EMAIL, LOGIN_PASSWORD, LOGIN_END = range(3)
LOGIN_URL = Config.BASE_URL + Config.url_path['login']


def do_login_email(update, context):
    context.user_data['email'] = update.message.text

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Введите пароль:'
    )
    return LOGIN_PASSWORD


def do_login_auth(update, context):
    login_data = {
        'email': context.user_data['email'],
        'password': context.user_data['password']
    }

    user_info = requests.post(
        url=LOGIN_URL,
        data=login_data
    ).json()

    if user_info['auth']:
        context.user_data.update(user_info['user'])
        pprint(context.user_data)
        context.user_data['logged'] = True
        context.bot.sendMessage(
            chat_id=update.message.chat_id,
            text=f"Здравствуйте, { context.user_data['name'] } { context.user_data['patronymic'] }. Вы авторизованы."
        )

    else:

        if 'message' in context.user_data.keys():
            if 'message' == "User didn't activated account.":
                context.bot.sendMessage(
                    chat_id=update.message.chat_id,
                    text="Вы не активировали свой аккаунт Проектного Офиса ИКТИБ."
                )

        else:
            context.bot.sendMessage(
                chat_id=update.message.chat_id,
                text="Что-то пошло не так, попробуйте еще раз или позже."
            )

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
        text='* сообщение с паролем удалено *'
    )

    return do_login_auth(update, context)


def do_login(update, context):
    if len(context.args) > 2:
        context.bot.delete_message(
            chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Передано больше двух аргументов. Сообщение удалено, т.к. оно могло содержать пароль\n\n' +
                 'Используя команду /login, вводите только электронную почту и пароль.'
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
            text='Введите пароль:'
        )
        return LOGIN_PASSWORD

    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите вашу электронную почту:'
        )
        return LOGIN_EMAIL


dp.add_handler(
    ConversationHandler(
        entry_points=[
            CommandHandler(command='login', callback=do_login, pass_args=True)
        ],
        states={
            LOGIN_EMAIL: [MessageHandler(filters=Filters.text, callback=do_login_email)],
            LOGIN_PASSWORD: [MessageHandler(filters=Filters.text, callback=do_login_password)]
        },
        fallbacks=[]
    )
)
