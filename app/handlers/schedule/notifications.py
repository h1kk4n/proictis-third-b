import datetime
import pytz

from app.handlers.schedule.shedule_handler import get_schedule, banned_lecture_list
from app import dp


def send_schedule_notification(context):
    bot_message = f'Через 20 минут у вас по расписанию начинается {context.job.name}, держу в курсе'

    dp.bot.send_message(
        chat_id=context.job.context.tg_chat_id,
        text=bot_message
    )


def make_schedule_notification(user, lecture, day, time, job_queue):
    lecture_hour, lecture_minute = time.split('-')[0].split(':')
    lecture_hour = int(lecture_hour)
    lecture_minute = int(lecture_minute) - 20
    if lecture_minute < 0:
        lecture_hour = lecture_hour - 1
        lecture_minute = lecture_minute % 60

    necessary_time = datetime.datetime(
        year=day.year,
        month=day.month,
        day=day.day,
        hour=lecture_hour,
        minute=lecture_minute,
        tzinfo=pytz.timezone('Etc/GMT-3')
    )

    if lecture and necessary_time > day and lecture not in banned_lecture_list:
        job_queue.run_once(
            callback=send_schedule_notification,
            when=necessary_time,
            context=user,
            name=lecture
        )


def schedule_notifications_job(context, user=None):
    try:
        user = context.job_queue.context
    except AttributeError:
        pass
    finally:
        schedule = ''
        if user.role == 'student':
            schedule = get_schedule(user.group)['table']['table']
        elif user.role == 'mentor':
            schedule = get_schedule(user.surname)['table']['table']

        day = datetime.datetime.now(pytz.timezone('Etc/GMT-3'))
        weekday = datetime.datetime.weekday(day)
        day_schedule = schedule[weekday + 2]
        time_schedule = schedule[1]

        for i in range(1, len(day_schedule)):
            time = time_schedule[i]
            lecture = day_schedule[i]
            make_schedule_notification(user, lecture, day, time, job_queue)


if __name__ == '__main__':
    pass
