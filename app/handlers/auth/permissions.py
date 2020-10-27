from config import Config
from app.db.db import Session
from app.db.models import User


def get_user_info(update):
    session = Session()
    user = session.query(User).filter(User.tg_chat_id == update.message.chat_id).first()
    session.close()
    return user


# Checks user status
def is_owner(update):
    return Config.OWNER_TG_ID == update.message.chat_id


def is_admin(update):
    user_stats = get_user_info(update)
    if user_stats:
        return user_stats.is_admin
    return is_owner(update)


def check_admin_status(update, context):
    if is_admin(update):
        return True
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='У вас нет таких прав. Вы не авторизованы'
        )
        return False


def not_enough_permission(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Вы не являетесь администратором, потому не имеете права использовать эту функцию'
    )

