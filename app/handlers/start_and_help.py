from telegram.ext import CommandHandler

from app import dp
from app.handlers.auth.permissions import is_admin

help_replica = {
    'ordinary_help': '''<b><i>Здраствуй, тебя приветствует чат-бот проектного офиса ИКТИБ.</i></b>
<i>Для более продуктивной работы советую тебе авторизоваться через сайт проектного офиса</i>
Просто напиши мне - /login
Если же ты не зарегистрирован на сайте проектного офиса, напиши мне - /register
Чтобы узнать свои данные - используй команду /profile

/start, /help выведут это сообщение

<i>Если тебе интересна информация о проектном офисе, можешь воспользоваться следующими функциями</i>
/mentors – Список наставников
/project - Список проектов
/news - Последние новости
/manual - Руководство по проекту
/contacts - Контакты
/achieves - Достижение студентов
/contests - Актуальные конкурсы

Так же ты можешь узнать свое расписание - просто напиши мне /schedule
Если ты уже авторизовался то я буду напоминать тебе о начале пары за 20 минут до ее начала, 
не забудь в личном кабинете проектного офиса указать свою группу. 

<i>На данный момент бот не может узнать, обновил ли ты информацию на сайте</i>, так что для вступления 
новых данных в силу необходимо ввести команду /logout и повторно авторизоваться\n
''',
    'admin_help': '''<b><i>Админ-панель</i></b>:
/newadmin - добавить нового модератора
/deladmin - убрать пользователя из списка модераторов

/notestudent - написать сообщение всем студентам в боте

/dbrefill - перезаполнить таблицы проектов (перезаполнит данные для функции /project, использовать в случае, если 
появились новые проекты и сформировались команды)
/dropusers - сбросить таблицу пользователей\n
''',
    'help_end': 'Если все понятно - напиши мне'

}


def do_start_and_help(update, context):
    help_message = help_replica['ordinary_help']

    if is_admin(update):
        help_message += help_replica['admin_help']

    help_message += help_replica['help_end']

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=help_message
    )


dp.add_handler(CommandHandler(command=['start', 'help'], callback=do_start_and_help))

