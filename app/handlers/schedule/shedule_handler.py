import requests
import os
import json
import datetime
import pytz
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from pprint import pprint

from app import dp
from app.db.db import Session
from app.db.models import User
from config import Config


schedule_buttons = {
    'choice': 'schedule_choice',
    'back': 'schedule_back',
    'forward': 'schedule_forward',
    'week': 'schedule_week',
    'day': 'schedule_day',
    'all': 'schedule_all',
    'end': 'schedule_end'
}

banned_lecture_list = [
    'пр.Основы проектной деятельности Федотова А. Ю. И-241',
    'пр.Основы проектной деятельности Эксакусто Т. В. И-241'
]


class ScheduleException(BaseException):
    def __init__(self):
        pass


class ChoicesException(ScheduleException):
    def __init__(self, choices_schedule):
        self.choices_schedule = choices_schedule['choices']


class NoEntriesException(ScheduleException):
    def __init__(self):
        self.text = 'По вашему запросу ничего не найдено (возможно, сервис лег)'


class WentWrongException(ScheduleException):
    def __init__(self):
        self.text = 'Что-то пошло не так при выводе расписания'


schedule_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'groups')

FIND_GROUP = 0


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
            raise NoEntriesException

        elif response.get('choices', False):
            raise ChoicesException(response)

        else:
            raise WentWrongException

    except requests.exceptions.RequestException:
        group_dir = os.path.join(schedule_dir, request_data)
        week_files = sorted(os.listdir(group_dir))
        if not week_num:
            week_num = len(week_files) - 1
        week_file = os.path.join(group_dir, week_files[week_num])

        with open(week_file, 'r') as week_json_file:
            response = json.loads(week_json_file.read())

            return response


def find_group(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Введите интересующую вас группу/аудиторию/преподавателя'
    )


def make_schedule_message(schedule, group, week, nes_weekday, weekday_query):
    bot_message = f"<b><i>Расписание {group}</i></b>\n" \
                  f"<b>Неделя {week}</b>\n\n" \
                  f"<b>Пары</b> ({nes_weekday}):\n\n"

    week_schedule = ''
    counter = schedule['table']['table'][0]
    timer = schedule['table']['table'][1]
    lectures = schedule['table']['table'][weekday_query + 2]
    for i in range(1, len(schedule['table']['table'][0])):

        lecture = lectures[i].replace('<', '').replace('>', '')
        if lecture and lecture not in banned_lecture_list:
            week_schedule += f"<b>{counter[i]}</b> ({timer[i]}): {lecture}\n\n"
        else:
            week_schedule += f"<b>{counter[i]}</b> ({timer[i]}): *отсутствует*\n\n"

    bot_message += week_schedule
    return bot_message


def make_group_schedule(update, context, group_query, weekday_query=0, week_num=None):
    try:
        schedule = get_schedule(group_query, week_num)

    except ChoicesException as e:
        schedule = e.choices_schedule

        bot_message = 'Возможно вы имели в виду:'

        keyboard_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text=f"{group['name']}",
                callback_data=f"{schedule_buttons['choice']}: {group['name']}"

            )] for group in schedule
        ])

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=bot_message,
            reply_markup=keyboard_markup
        )

    except NoEntriesException as e:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=e.text
        )

    except WentWrongException as e:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=e.text
        )

    else:
        query = update.callback_query

        group = schedule['table']['name']
        week = schedule['table']['week']

        keyboard_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text='<-',
                        callback_data=f'{schedule_buttons["back"]}: {group} {week} {weekday_query}'
                    ),
                    InlineKeyboardButton(
                        text='Текущая неделя',
                        callback_data=f'{schedule_buttons["week"]}: {group} {week}'
                    ),
                    InlineKeyboardButton(
                        text='->',
                        callback_data=f'{schedule_buttons["forward"]}: {group} {week} {weekday_query}'
                    )
                ],
                [
                    InlineKeyboardButton(text='Все недели', callback_data=f'{schedule_buttons["all"]}: { group }')
                ]
            ]
        )

        if weekday_query == 6:
            if query is None:
                context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text='Воскресенье, поздравляю, пар нет)',
                    reply_markup=keyboard_markup
                )
            else:
                context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text='Воскресенье, поздравляю, пар нет)',
                    reply_markup=keyboard_markup
                )

        elif 0 <= weekday_query <= 5:
            nes_weekday = schedule['table']['table'][weekday_query + 2][0]

            bot_message = make_schedule_message(schedule, group, week, nes_weekday, weekday_query)

            if query is None:
                context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=bot_message,
                    reply_markup=keyboard_markup
                )
            else:
                context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text=bot_message,
                    reply_markup=keyboard_markup
                )

        elif weekday_query > 6 or weekday_query < 0:
            add_weeks = weekday_query // 7
            weekday_query = weekday_query % 7

            nes_week = schedule['table']['week'] + add_weeks

            if nes_week in schedule['weeks']:
                make_group_schedule(update, context, group_query, weekday_query, nes_week)

            else:
                if query is None:
                    context.bot.send_message(
                        chat_id=update.message.chat_id,
                        text="Расписания либо еще нет, либо уже не будет. Попробуйте позже",
                        reply_markup=keyboard_markup
                    )
                else:
                    context.bot.edit_message_text(
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        text="Расписания либо еще нет, либо уже не будет. Попробуйте позже",
                        reply_markup=keyboard_markup
                    )


def choose_schedule_group(update, context):
    week_day = datetime.datetime.weekday(datetime.datetime.now(pytz.timezone('Etc/GMT-3')))

    query = update.callback_query

    group = query.data.replace(f'{schedule_buttons["choice"]}: ', '')

    make_group_schedule(update, context, group, week_day)


def show_schedule(update, context):
    week_day = datetime.datetime.weekday(datetime.datetime.now(pytz.timezone('Etc/GMT-3')))

    session = Session()
    user = session.query(User).filter(User.tg_chat_id == update.message.chat_id).first()
    if user:
        group = user.group
        make_group_schedule(update, context, group, week_day)
        return ConversationHandler.END

    elif len(context.args) == 0:
        find_group(update, context)
        return FIND_GROUP

    elif len(context.args) == 1:
        group_query = context.args[0]
        message_id = update.message.message_id + 1
        context.user_data['group_query' + str(message_id)] = group_query

        make_group_schedule(update, context, group_query, week_day)

        return ConversationHandler.END

    else:
        return ConversationHandler.END


# Schedule arrows
def change_day_schedule(update, context, week_day):
    query = update.callback_query

    group_query = query.data.split()[1:-2]
    week = int(query.data.split()[-2])

    make_group_schedule(update, context, group_query, week_day, week)


def schedule_back(update, context):
    query = update.callback_query

    week_day = int(query.data.split()[-1]) - 1
    change_day_schedule(update, context, week_day)


# Searching for query
def schedule_forward(update, context):
    query = update.callback_query

    week_day = int(query.data.split()[-1]) + 1
    change_day_schedule(update, context, week_day)


def schedule_group_founded(update, context):
    group_query = update.message.text
    week_day = datetime.datetime.weekday(datetime.datetime.now(pytz.timezone('Etc/GMT-3')))

    make_group_schedule(update, context, group_query, week_day)
    return ConversationHandler.END


# Current week schedule
def schedule_weekdays(update, context):
    query = update.callback_query

    group = query.data.split()[1]
    nes_week = int(query.data.split()[2])

    schedule = get_schedule(group, nes_week)

    bot_message = f"<b><i>Расписание {schedule['table']['name']}\n</i></b>" \
                  f"<b>Неделя {schedule['table']['week']}:</b>"

    week_keyboard = []

    for i in range(2, 8):
        week_keyboard.append(
          [InlineKeyboardButton(
            text=schedule['table']['table'][i][0],
            callback_data=f"{schedule_buttons['day']}: {schedule['table']['name']} {schedule['table']['week']} {i - 2}"
          )]
        )

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=bot_message,
        reply_markup=InlineKeyboardMarkup(week_keyboard)
    )


def schedule_from_week(update, context):
    query = update.callback_query

    data = query.data.split()

    group = data[1]
    week = int(data[-2])
    weekday = int(data[-1])

    make_group_schedule(update, context, group, weekday, week)


# All weeks
def show_all_schedule_weeks(update, context):
    query = update.callback_query

    data = query.data.split()

    group = data[1]

    schedule = get_schedule(group)

    reply_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(
                text=f'Неделя {week_num}',
                callback_data=f'{schedule_buttons["week"]}: {group} {week_num}'
            )] for week_num in schedule['weeks']
        ]
    )

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f'<b><i>Расписание {group}</i></b>:',
        reply_markup=reply_keyboard
    )


# End schedule
def schedule_end(update, context):
    query = update.callback_query

    context.bot.edit_message_reply_markup(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=None
    )


dp.add_handler(CallbackQueryHandler(pattern=schedule_buttons["choice"], callback=choose_schedule_group))
dp.add_handler(CallbackQueryHandler(pattern=schedule_buttons["back"], callback=schedule_back))
dp.add_handler(CallbackQueryHandler(pattern=schedule_buttons["forward"], callback=schedule_forward))
dp.add_handler(CallbackQueryHandler(pattern=schedule_buttons["week"], callback=schedule_weekdays))
dp.add_handler(CallbackQueryHandler(pattern=schedule_buttons["day"], callback=schedule_from_week))
dp.add_handler(CallbackQueryHandler(pattern=schedule_buttons["all"], callback=show_all_schedule_weeks))
dp.add_handler(CallbackQueryHandler(pattern=schedule_buttons["end"], callback=schedule_end))

dp.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler(command='schedule', callback=show_schedule, pass_args=True)],
        states={
            FIND_GROUP: [MessageHandler(filters=Filters.text, callback=schedule_group_founded)]
        },
        fallbacks={}
    )
)

if __name__ == '__main__':
    pprint(get_schedule('ктсо2-5'))
