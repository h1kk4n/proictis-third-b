from app import updater
from config import Config

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    updater.bot.send_message(
        chat_id=298424246,
        text='Бот включен. Привет, <a href="tg://user?id=298424246">немолодой</a>'
    )

    '''updater.start_webhook(
        listen='0.0.0.0',
        port=int(Config.PORT),
        url_path=Config.TOKEN
    )
    updater.bot.set_webhook('https://warm-headland-36871.herokuapp.com/'+Config.TOKEN)'''

    updater.start_polling()

    updater.idle()
