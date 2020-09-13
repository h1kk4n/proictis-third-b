import requests
import urllib.parse
import os
import json
import datetime
import pytz
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext import ConversationHandler
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from pprint import pprint

from app import dp
from config import Config


class ScheduleException(BaseException):
    def __ini__(self):
        pass


schedule_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'groups')


def get_schedule(request_data, week_num=None):
    try:
        if not os.path.exists(schedule_dir):
            os.mkdir(schedule_dir)

        response = requests.get(Config.schedule_url, params={'query': request_data})
        response.raise_for_status()

        response = response.json()

        if response.get('table', False):

            group = response['table']['group']
            if week_num is not None:
                response = requests.get(Config.schedule_url, params={'group': group, 'week': week_num}).json()

            # Checks if schedule if for students group, teacher or audience
            if group.startswith('a'):
                group_dir = os.path.join(schedule_dir, 'audiences')
            elif group.startswith('m'):
                group_dir = os.path.join(schedule_dir, 'teachers')
            else:
                group_dir = os.path.join(schedule_dir, 'students')
            if not os.path.exists(group_dir):
                os.mkdir(group_dir)

            file_name = response['table']['name']
            group_dir = os.path.join(group_dir, file_name)
            if not os.path.exists(group_dir):
                os.mkdir(group_dir)

            week_file = os.path.join(group_dir, f"week{response['table']['week']}.json")
            with open(week_file, 'w') as week_json_file:
                week_json_file.write(json.dumps(response))

            return response

        elif response.get('result', False) == 'no_entries':
            raise ScheduleException

        elif response.get('choices', False):
            raise ScheduleException

        else:
            raise ScheduleException

    except requests.RequestException:
        group_dir = os.path.join(schedule_dir, request_data)
        week_files = sorted(os.listdir(group_dir))
        week_file = os.path.join(group_dir, week_files[week_num - 1])

        with open(week_file, 'r') as week_json_file:
            response = json.loads(week_json_file.read())

            return response


def find_group(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Введите интересующую вас группу/аудиторию/преподавателя'
    )


def make_group_schedule(update, context, group_query):
    try:
        schedule = get_schedule(group_query)
    except ScheduleException:
        pass
    else:

        week_day = datetime.datetime.weekday(datetime.datetime.now(pytz.timezone('Europe/Moscow')))

        bot_message = f"<b><i>Расписание { schedule['table']['name'] }</i></b>\n" \
                      f"<b>Неделя { schedule['table']['week'] }</b>\n\n" \
                      f"<b>{ schedule['table']['table'][0][0] }</b> " \
                      f"({ schedule['table']['table'][week_day + 2][0] }):\n\n"

        if week_day == 6:
            bot_message += 'Сегодня воскресенье, поздравляю, пар нет)'

        elif 0 <= week_day <= 5:
            week_schedule = ''
            counter = schedule['table']['table'][0]
            timer = schedule['table']['table'][1]
            lectures = schedule['table']['table'][week_day + 2]
            for i in range(1, len(schedule['table']['table'][0])):
                lecture = lectures[i].replace('<', '').replace('>', '')

                week_schedule += f"<b>{ counter[i] }</b> ({ timer[i] }): { lecture or ' <i>отсутствует</i>' }\n\n"

            bot_message += week_schedule

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=bot_message
        )


def show_schedule(update, context):
    if len(context.args) == 0 and context.user_data.get('group', True):
        find_group(update, context)
    elif len(context.args) == 1:
        group_query = context.args[0]
        make_group_schedule(update, context, group_query)

    else:
        pass


dp.add_handler(CommandHandler(command='schedule', callback=show_schedule, pass_args=True))

'''dp.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler(command='schedule', callback=show_schedule, pass_args=True)],
        states={},
        fallbacks={}
    ))'''

if __name__ == '__main__':
    pprint(get_schedule('ктсо2-5'))
