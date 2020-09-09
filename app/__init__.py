from telegram.ext import Updater, Defaults

from config import Config


updater = Updater(
    token=Config.TOKEN,
    defaults=Defaults(
        parse_mode="HTML",
        disable_web_page_preview=1,
    ),
    use_context=True
)

dp = updater.dispatcher

from app.handlers.routes import achievements_handler, news_handler, contests_handler, mentors_handler
from app.handlers import start_and_help, login_handler, manual_handler
from app.handlers.schedule import shedule_handler
from app.handlers.projects import projects_handler


