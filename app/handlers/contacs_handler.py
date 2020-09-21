#Не реализовал текст приветствия команды и как и в мануале подключение файлов через os
import os.path
from telegram.ext import InlineKeyboardButton
from telegram.ext import InlineKeyboardMarkup
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler

CALLBACK_BUTTON1 = "callback_button1"
CALLBACK_BUTTON2 = "callback_button2"
CALLBACK_BUTTON3 = "callback_button3"

TITLES = {
  CALLBACK_BUTTON1: "Плёнкин Антон Павлович",
  CALLBACK_BUTTON2: "Федотова Анна Юрьевна",
  CALLBACK_BUTTON3: "Самойленко Валерия Сергеевна",
}

def get_contacs_keyboard():
  keyboard = [
    [InlineKeyboardButton(TITLES[CALLBACK_BUTTON1], callback_data=CALLBACK_BUTTON1)],
    [InlineKeyboardButton(TITLES[CALLBACK_BUTTON2], callback_data=CALLBACK_BUTTON2)],
    [InlineKeyboardButton(TITLES[CALLBACK_BUTTON2], callback_data=CALLBACK_BUTTON2)],
    ]
  return InlineKeyboardMarkup(keyboard)

def keyboard_callback_handler(bot: Bot, update: Update, chat_data=None, **kwargs):
  query = update.callback_query
  data = query.data
  now = datetime.datetime.now()
  
  chat_id = update.effective_message.chat_id
  current_text = update.effective_message.text
  
  if data = CALLBACK_BUTTON1:
        query.edit_message_text(
            text = "",
            chat = chat_id,
            reply_markup=get_contacs_keyboard(),
            )
  elif data = CALLBACK_BUTTON2:
        query.edit_message_text(
            text = "",
            chat = chat_id,
            reply_markup=get_contacs_keyboard(),
            )
  elif data = CALLBACK_BUTTON3:
        query.edit_message_text(
            text = "",
            chat = chat_id,
            reply_markup=get_contacs_keyboard(),
            )
