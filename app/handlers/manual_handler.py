# БЕТА, БУДУ ПЕРЕПРОВЕРЯТЬ, НЕ БЫЛО ВОЗМОЖНОСТИ ПРОВЕРИТЬ НА БОТЕ
import os.path
from telegram.ext import InlineKeyboardButton
from telegram.ext import InlineKeyboardMarkup
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler

CALLBACK_BUTTON1 = "callback_button1"
CALLBACK_BUTTON2 = "callback_button2"
CALLBACK_BUTTON3 = "callback_button3"
CALLBACK_BUTTON4 = "callback_button4"
CALLBACK_BUTTON5 = "callback_button5"
CALLBACK_BUTTON6 = "callback_button6"

TITLES = {
  CALLBACK_BUTTON1: "О проектном офисе",
  CALLBACK_BUTTON2: "Организация ТП 1 курс",
  CALLBACK_BUTTON3: "Организация ТП 2 курс",
  CALLBACK_BUTTON4: "Требование к оформлению проекта",
  CALLBACK_BUTTON5: "Наставники",
  CALLBACK_BUTTON6: "Проекты",
  CALLBACK_BUTTON7: "Обратно",
}

def get_navmenu_keyboard():
    keyboard = [
        [InlineKeyboardButton(TITLES[CALLBACK_BUTTON7], callback_data=CALLBACK_BUTTON7),],
    ]

def get_manual_keyboard():
  keyboard = [
        [InlineKeyboardButton(TITLES[CALLBACK_BUTTON1], callback_data=CALLBACK_BUTTON1),],
        [InlineKeyboardButton(TITLES[CALLBACK_BUTTON2], callback_data=CALLBACK_BUTTON2),],
        [InlineKeyboardButton(TITLES[CALLBACK_BUTTON3], callback_data=CALLBACK_BUTTON3),],
        [InlineKeyboardButton(TITLES[CALLBACK_BUTTON4], callback_data=CALLBACK_BUTTON4),],
        [InlineKeyboardButton(TITLES[CALLBACK_BUTTON5], callback_data=CALLBACK_BUTTON5),],
        [InlineKeyboardButton(TITLES[CALLBACK_BUTTON6], callback_data=CALLBACK_BUTTON6),],
  ]
  return InlineKeyboardMarkup(keyboard)

def do_manual(update, context):
    bot.send_message(
        chat = chat_id,
        text = "<b>Мануал:<b>";
        reply_markup = get_manual_keyboard(),
    )

def keyboard_callback_handler(bot: Bot, update: Update, chat_data=None, **kwargs):
  query = update.callback_query
  data = query.data
  now = datetime.datetime.now()
  
  chat_id = update.effective_message.chat_id
  current_text = update.effective_message.text
  
  if data = CALLBACK_BUTTON1:
        query.edit_message_text(
            text = ,
            chat = chat_id,
            reply_markup=get_navmenu_keyboard(),
        )
        if data = CALLBACK_BUTTON7:
            query.edit_message_text(
                text = "<b>Мануал:<b>",
                reply_markup = get_manual_keyboard(),
            )

  elif data = CALLBACK_BUTTON2:
        query.edit_message_text(
            text = ,
            chat = chat_id,
            reply_markup=get_navmenu_keyboard(),
        )
        if data = CALLBACK_BUTTON7:
            query.edit_message_text(
                text = "<b>Мануал:<b>",
                reply_markup = get_manual_keyboard(),
            )
  elif data = CALLBACK_BUTTON3:
        query.edit_message_text(
            text = ,
            chat = chat_id,
            reply_markup=get_navmenu_keyboard(),
        )
        if data = CALLBACK_BUTTON7:
            query.edit_message_text(
                text = "<b>Мануал:<b>",
                reply_markup = get_manual_keyboard(),
            )
  elif data = CALLBACK_BUTTON4:
        query.edit_message_text(
            text = ,
            chat = chat_id,
            reply_markup=get_navmenu_keyboard(),
        )
        if data = CALLBACK_BUTTON7:
            query.edit_message_text(
                text = "<b>Мануал:<b>",
                reply_markup = get_manual_keyboard(),
            )
  elif data = CALLBACK_BUTTON5:
        query.edit_message_text(
            text = ,
            chat = chat_id,
            reply_markup=get_navmenu_keyboard(),
        )
        if data = CALLBACK_BUTTON7:
            query.edit_message_text(
                text = "<b>Мануал:<b>",
                reply_markup = get_manual_keyboard(),
            )
  elif data = CALLBACK+BUTTON6:
        query.edit_message_text(
            text = ,
            chat = chat_id,
            reply_markup=get_navmenu_keyboard(),
        )
        if data = CALLBACK_BUTTON7:
            query.edit_message_text(
                text = "<b>Мануал:<b>",
                reply_markup = get_manual_keyboard(),
            )


dp.add_handler(CommandHandler(command='manual', callback=get_manual_keyboard))
dp.add_handler(CallbackQueryHandler(pattern=r'callback_button\d', callback=keyboard_callback_handler))

