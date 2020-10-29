# Не реализовал текст приветствия команды и как и в мануале подключение файлов через os
import os
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler

from app import dp

contacts_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'text')
contacts_buttons = {
    button_name.split()[0]: button_name.replace('.txt', '') for button_name in os.listdir(contacts_dir)
}


def get_contacts_keyboard():
    keyboard = [
        [InlineKeyboardButton(text, callback_data=button)]
        for button, text in contacts_buttons
    ]
    return InlineKeyboardMarkup(keyboard)


def do_contacts(update, context):
    chat_id = update.message.chat_id
    files = [
        os.path.join(contacts_dir, text + '.txt')
        for data, text in contacts_buttons.items()
    ]
    for file in files:
        with open(file, 'r', encoding='utf8') as f:
            photo = f.readline()
            text = f.read()
            context.bot.send_photo(
                photo=photo,
                chat_id=chat_id,
                caption=text
            )


dp.add_handler(CommandHandler(command='contacts', callback=do_contacts))
