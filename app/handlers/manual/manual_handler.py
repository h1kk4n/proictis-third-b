# БЕТА, БУДУ ПЕРЕПРОВЕРЯТЬ, НЕ БЫЛО ВОЗМОЖНОСТИ ПРОВЕРИТЬ НА БОТЕ
# Файлы не подтянул пока что, но они лежал в папке manual
import os.path
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler

from app import dp

manual_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sections')
manual_buttons = {
    f"s{number}": button_name.replace('.txt', '') for number, button_name in enumerate(os.listdir(manual_dir))
}


def get_manual_keyboard():
    keyboard = [
        [InlineKeyboardButton(text=button_text, callback_data=f"manual: {button_data}")]
        for button_data, button_text in manual_buttons.items()
    ]
    return InlineKeyboardMarkup(keyboard)


def do_manual(update, context):
    query = update.callback_query

    if query is None:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="<b><i>Мануал:</i></b>",
            reply_markup=get_manual_keyboard(),
        )
    else:
        context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="<b><i>Мануал:</i></b>",
            reply_markup=get_manual_keyboard(),
        )


def do_manual_section(update, context):
    query = update.callback_query
    data = query.data.replace('manual: ', '')

    chat_id = query.message.chat_id
    message_id = query.message.message_id
    section = os.path.join(manual_dir, manual_buttons[data] + '.txt')
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text='Назад', callback_data='back_to_manual')]]
    )

    with open(section, encoding='utf8') as f:
        section_text = f.read()
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=section_text,
            reply_markup=keyboard
        )


dp.add_handler(CommandHandler(command='manual', callback=do_manual))
dp.add_handler(CallbackQueryHandler(pattern='back_to_manual', callback=do_manual))
dp.add_handler(CallbackQueryHandler(pattern='manual', callback=do_manual_section))

if __name__ == '__main__':
    print(manual_buttons)
