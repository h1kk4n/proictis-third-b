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
    if user_stats is not None:
        return is_owner(update) or user_stats.is_admin
    return is_owner(update)


def is_student(update=None, user=None):
    if update is not None:
        user_stats = get_user_info(update)
        return user_stats.role == 'student'
    if user is not None:
        return user.role == 'student'


def is_mentor(update=None, user=None):
    if update is not None:
        user_stats = get_user_info(update)
        return user_stats.role == 'mentor'
    if user is not None:
        return user.role == 'mentor'


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

