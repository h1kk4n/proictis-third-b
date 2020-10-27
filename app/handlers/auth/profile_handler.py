from telegram.ext import CommandHandler

from app.handlers.auth.permissions import get_user_info
from app import dp


def do_profile(update, context):
    user = get_user_info(update)
    if user:
        bot_message = str(user)

        context.bot.send_message(
            chat_id=user.tg_chat_id,
            text=bot_message
        )
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Вы не авторизованы'
        )


dp.add_handler(CommandHandler(command='profile', callback=do_profile))