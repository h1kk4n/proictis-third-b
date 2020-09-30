from telegram.ext import CommandHandler

from app import dp
from app.db.db import fully_refill_database


def admin_db_refill(update, context):
    if update.message.chat_id == 298424246:
        bot_message = fully_refill_database()

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=bot_message
        )


dp.add_handler(CommandHandler(command='dbrefill', callback=admin_db_refill))