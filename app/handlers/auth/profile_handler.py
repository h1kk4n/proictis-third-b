from telegram.ext import CommandHandler

from app.db.models import User
from app.db.db import Session
from app import dp


def do_profile(update, context):
    try:
        session = Session()

        user = session.query(User).filter(User.tg_chat_id == update.message.chat_id).first()

        bot_message = str(user)

        context.bot.send_message(
            chat_id=user.tg_chat_id,
            text=bot_message
        )

        session.close()

    except:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Вы не авторизованы"
        )


dp.add_handler(CommandHandler(command='profile', callback=do_profile))