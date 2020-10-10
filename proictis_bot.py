from app import updater, dp
from config import Config
from app.db.db import Session
from app.db.models import User
from app.handlers.schedule.notifications import schedule_notifications_job, send_schedule_notification

import datetime
import pytz
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def restore_notifications():
    session = Session()

    users = session.query(User).all()

    for user in users:
        if user.is_notified:
            schedule_notifications_job(dp, user)
            dp.job_queue.run_daily(
                schedule_notifications_job,
                time=datetime.time(hour=1, minute=0, tzinfo=pytz.timezone('Etc/GMT-3')),
                days=(0, 1, 2, 3, 4, 5),
                context=user,
                name='Обновить расписание'
            )

    session.close()


if __name__ == '__main__':
    updater.bot.send_message(
        chat_id=Config.OWNER_TG_ID,
        text=f'Бот включен. Привет, <a href="tg://user?id={Config.OWNER_TG_ID}">немолодой</a>'
    )

    restore_notifications()

    if Config.APP_URL:
        updater.start_webhook(
            listen='0.0.0.0',
            port=int(Config.PORT),
            url_path=Config.TOKEN
        )
    
        updater.bot.set_webhook(Config.APP_URL+Config.TOKEN)

    else:
        updater.start_polling()

    updater.idle()
