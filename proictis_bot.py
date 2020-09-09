from app import updater

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    updater.bot.send_message(
        chat_id=298424246,
        text='Бот включен'
    )

    updater.start_polling()
    updater.idle()
