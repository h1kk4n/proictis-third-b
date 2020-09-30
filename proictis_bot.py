from app import updater
from config import Config

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    updater.bot.send_message(
        chat_id=Config.OWNER_TG_ID,
        text=f'Бот включен. Привет, <a href="tg://user?id={Config.OWNER_TG_ID}">немолодой</a>'
    )

    '''updater.start_webhook(
        listen='0.0.0.0',
        port=int(Config.PORT),
        url_path=Config.TOKEN
    )
    updater.bot.set_webhook('https://warm-headland-36871.herokuapp.com/'+Config.TOKEN)'''

    updater.start_polling()

    updater.idle()
