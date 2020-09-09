from dotenv import load_dotenv
import os

basedir = os.path.abspath(os.path.dirname(__file__))

env_path = os.path.join(basedir, ".env")
if os.path.exists(env_path):
    load_dotenv(verbose=True, dotenv_path=env_path)


class Config:
    TOKEN = os.environ.get("BOT_TOKEN", None)

    SQL_USER = os.environ.get("SQL_USER", None)
    SQL_PASS = os.environ.get("SQL_PASS", None)
    SQL_IP = os.environ.get("SQL_IP", None)
    SQL_PORT = os.environ.get("SQL_PORT", None)
    SQL_DB = os.environ.get("SQL_DB", None)
    DATABASE_URI = f'postgres+psycopg2://{SQL_USER}:{SQL_PASS}@{SQL_IP}:{SQL_PORT}/{SQL_DB}'

    BASE_URL = 'https://proictis.sfedu.ru'

    shedule_url = 'http://165.22.28.187/schedule-api/'

    url_path = {
        'contacts': '/about',
        'mentors': '/api/mentors',
        'projects': '/api/projects',
        'news': '/api/news',
        'competitions': '/api/competitions',
        'achievements': '/api/achievements',
        'login': '/api/login',
        'requests': '/api/me/requests',
        'archive': '/api/chat/archive',
        'chats': '/api/chats',
        'update': '/api/update',
        'me': '/api/me'
    }