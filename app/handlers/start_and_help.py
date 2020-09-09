from telegram.ext import CommandHandler

from app import dp


def do_start_and_help(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Привет, я чат-бот проектного офиса ИКТИБ команды ThirdB\n\n\
Вот что я могу:\n\
/login - Авторизация через сайт проектного офиса\n\
/mentors – Список наставников\n\
/calendar - Расписание\n\
/project - Список проектов\n\
/news - Последние новости\n\
/manual - Руководство по проекту\n\
/achieves - Достижение студентов\n\
/contests - Актуальные конкурсы\n\
/contacts - Контакты\n\n\
Так же есть функции только для наставников проектного офиса:\n\
/addevent – добавить мероприятие в расписание студентов\n\
/message – отправить сообщение студентам\n\
/change – изменить расписание\n\
Если все понятно напиши мне что-нибудь'
    )


dp.add_handler(CommandHandler(command=['start', 'help'], callback=do_start_and_help))

