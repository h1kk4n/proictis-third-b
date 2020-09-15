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
from config import Config


class ScheduleException(BaseException):
    def __init__(self, error_text='Что-то пошло не так при выводе расписания'):
        self.text = error_text


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
            raise ScheduleException('По вашему запросу ничего не найдено')

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


def make_group_schedule(update, context, group_query, weekday_query=0, week_num=None):
    try:
        schedule = get_schedule(group_query, week_num)

    except ScheduleException as e:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=e.text
        )

    else:

        group = schedule['table']['name']
        week = schedule['table']['week']

        keyboard_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text='<-', callback_data=f'schedule_back: {group} {week} {weekday_query}'),
                    InlineKeyboardButton(text='Текущая неделя', callback_data=f'schedule_week: {group} {week}'),
                    InlineKeyboardButton(text='->', callback_data=f'schedule_forward {group} {week} {weekday_query}')
                ],
                [
                    InlineKeyboardButton(text='Все недели', callback_data=f'schedule_all: { group }'),
                    InlineKeyboardButton(text='Закончить', callback_data='schedule_end')
                ]
            ]
        )

        if weekday_query == 6:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text='Воскресенье, поздравляю, пар нет)',
                reply_markup=keyboard_markup
            )

        elif 0 <= weekday_query <= 5:
            nes_weekday = schedule['table']['table'][weekday_query + 2][0]

            bot_message = f"<b><i>Расписание { group }</i></b>\n" \
                          f"<b>Неделя { week }</b>\n\n" \
                          f"<b>Пары</b> ({ nes_weekday }):\n\n"

            week_schedule = ''
            counter = schedule['table']['table'][0]
            timer = schedule['table']['table'][1]
            lectures = schedule['table']['table'][weekday_query + 2]
            for i in range(1, len(schedule['table']['table'][0])):
                lecture = lectures[i].replace('<', '').replace('>', '')

                week_schedule += f"<b>{ counter[i] }</b> ({ timer[i] }): { lecture or ' <i>отсутствует</i>' }\n\n"

            bot_message += week_schedule

            context.bot.send_message(
                chat_id=update.message.chat_id,
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
                context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text="Расписания либо еще нет, либо уже не будет. Попробуйте позже",
                    reply_markup=keyboard_markup
                )


def show_schedule(update, context):
    week_day = datetime.datetime.weekday(datetime.datetime.now(pytz.timezone('Europe/Moscow')))

    if context.user_data.get('group', None):
        group = context.user_data['group']
        print(group)
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

    group_query = query.data.split()[1]
    week = int(query.data.split()[2])

    context.bot.delete_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id
    )

    make_group_schedule(query, context, group_query, week_day, week)


def schedule_back(update, context):
    query = update.callback_query

    week_day = int(query.data.split()[3]) - 1
    change_day_schedule(update, context, week_day)


# Searching for query
def schedule_forward(update, context):
    query = update.callback_query

    week_day = int(query.data.split()[3]) + 1
    change_day_schedule(update, context, week_day)


def schedule_group_founded(update, context):
    group_query = update.message.text
    week_day = datetime.datetime.weekday(datetime.datetime.now(pytz.timezone('Europe/Moscow')))

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

    for i in range(2, 8
                   ):
        week_keyboard.append(
            [InlineKeyboardButton(
                text=schedule['table']['table'][i][0],
                callback_data=f"schedule_day: {schedule['table']['name']} {schedule['table']['week']} {i - 2}"
            )]
        )

    context.bot.delete_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
    )

    context.bot.send_message(
        chat_id=query.message.chat_id,
        text=bot_message,
        reply_markup=InlineKeyboardMarkup(week_keyboard)
    )


def schedule_from_week(update, context):
    query = update.callback_query

    data = query.data.split()

    group = data[1]
    week = int(data[2])
    weekday = int(data[3])

    context.bot.delete_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
    )

    make_group_schedule(query, context, group, weekday, week)


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
                callback_data=f'schedule_week: {group} {week_num}'
            )] for week_num in schedule['weeks']
        ]
    )

    context.bot.delete_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id
    )

    context.bot.send_message(
        chat_id=query.message.chat_id,
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


dp.add_handler(CallbackQueryHandler(pattern='schedule_back', callback=schedule_back))
dp.add_handler(CallbackQueryHandler(pattern='schedule_forward', callback=schedule_forward))
dp.add_handler(CallbackQueryHandler(pattern='schedule_week', callback=schedule_weekdays))
dp.add_handler(CallbackQueryHandler(pattern='schedule_day', callback=schedule_from_week))
dp.add_handler(CallbackQueryHandler(pattern='schedule_all', callback=show_all_schedule_weeks))
dp.add_handler(CallbackQueryHandler(pattern='schedule_end', callback=schedule_end))

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
