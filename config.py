from dotenv import load_dotenv
import os

basedir = os.path.abspath(os.path.dirname(__file__))

env_path = os.path.join(basedir, ".env")
if os.path.exists(env_path):
    load_dotenv(verbose=True, dotenv_path=env_path)


class Config:
    TOKEN = os.environ.get("BOT_TOKEN", None)

    OWNER_TG_ID = int(os.environ.get("OWNER_TG_ID", None))

    APP_URL = os.environ.get('APP_URL', None)
    PORT = int(os.environ.get('PORT', 5000))

    DATABASE_URL = os.environ.get('DATABASE_URL', None).replace('postres', 'postgres+psycopg2')

    GOOGLE_SERVICE_ACCOUNT = os.environ.get('GOOGLE_SERVICE_ACCOUNT', None)

    BASE_URL = 'https://proictis.sfedu.ru'

    schedule_url = 'http://165.22.28.187/schedule-api/'

    url_path = {
        'contacts': '/about',
        'mentors': '/api/mentors',
        'projects': '/api/projects',
        'sheets': '/api/projects/sheets',
        'news': '/api/news',
        'competitions': '/api/competitions',
        'achievements': '/api/achievements',
        'login': '/api/login',
        'register': '/api/register',
        'requests': '/api/me/requests',
        'archive': '/api/chat/archive',
        'chats': '/api/chats',
        'update': '/api/update',
        'me': '/api/me'
    }
