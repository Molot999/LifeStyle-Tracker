from telebot.types import Message
from config import bot
import dbconnection as db
from contexts import get_user_context, get_meal_diary_context, UserContext, MealDiaryContext
import datetime
from typing import List
from meal_diary_utils import get_month_str
from decorators import cancel_on_message_confusion
import keyboards
from user_timezone import convert_to_user_local_time, convert_to_db_time

def get_user_meal_diary_periods_list(user_meal_diary_periods, user_timezone):
    user_meal_diary_periods = list(user_meal_diary_periods)
    periods = {}
    for period_db_time_full in user_meal_diary_periods:
        period_local_time_full = convert_to_user_local_time(period_db_time_full, user_timezone)
        period_local_time_datetime = datetime.datetime.strptime(period_local_time_full, '%Y.%m.%d %H:%M')
        period_local_time_date = period_local_time_datetime.strftime('%d.%m.%Y')

        period_db_datetime = datetime.datetime.strptime(period_db_time_full, '%Y.%m.%d %H:%M')
        period_db_time_date = period_db_datetime.strftime('%Y.%m.%d')

        command = period_local_time_datetime.strftime("%d%m%Y")
        if command not in periods:
            periods[command] = (period_local_time_date, period_db_time_date)

    # Отсортируем словарь по ключам (датам) в формате "%d%m"
    periods = dict(
        sorted(
            periods.items(),
            key=lambda item: datetime.datetime.strptime(item[0], '%d%m%Y')
        )
    )
    return periods

def process_meal_diary(message:Message):
    user_id = db.get_user_id(message.chat.id)
    if user_meal_diary_periods := db.get_user_meal_diary_periods(user_id):
        user_timezone = db.get_user_timezone(user_id)
        periods = get_user_meal_diary_periods_list(user_meal_diary_periods, user_timezone or '+03:00')
        meal_diary_context:MealDiaryContext = get_meal_diary_context(message)
        meal_diary_context.periods = periods
        periods_str = 'Для просмотра дневника питания выберите соответствующий день нажатием на команду слева:'
        last_15_keys = list(periods.keys())[-15:]
        for key in last_15_keys:
            local_time, _ = periods[key]
            day, month, year = str(local_time).split('.')
            periods_str += f'\n/{key} {day} {get_month_str(month)}'
        if not bool(user_timezone):
            periods_str += 'Чтобы выводить результаты в соответствии с местным временем установите часовой пояс в разделе Профиль'
        bot.send_message(message.chat.id, periods_str, reply_markup=keyboards.meal_diary_keyboard())
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(message, period_handler)
    else:
        bot.send_message(message.chat.id, 'Вы еще не заносили записей в дневник питания')

@cancel_on_message_confusion
def period_handler(message:Message):
    if str(message.text).replace('/', '').isdigit():
        period = str(message.text).replace('/', '')
        meal_diary_context:MealDiaryContext = get_meal_diary_context(message)
        periods = meal_diary_context.periods
        if period_data := periods.get(period):
            _, db_time = period_data
            print_period_foods(message, db_time)
            return 
        else:
            bot.send_message(message.chat.id, 'Ошибка. Дневник питания не найден')
    else:
        bot.send_message(message.chat.id, 'Ошибка. Такой команды не существует')
        
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(message, period_handler)

def print_period_foods(message:Message, period_date):
    user_id = db.get_user_id(message.chat.id)
    if user_meal_period_data := db.get_user_meal_period_data(user_id, period_date):
        day_meal_diary_str = 'Список продуктов за данный день (Название - КБЖУ):'
        total_calories = 0.0
        total_protein = 0.0
        total_fat = 0.0
        total_carbohydrate = 0.0
        food_ids = []
        for food in user_meal_period_data:
            food_id = food.id
            food_ids.append(food_id)
            calories = food.calories
            total_calories += calories
            protein = food.protein
            total_protein += protein
            fat = food.total_fat
            total_fat += fat
            carbohydrate = food.total_carbohydrate
            total_carbohydrate += carbohydrate
            day_meal_diary_str += f'''\n/{food_id} {food.food_name} - {calories}/{protein}/{fat}/{carbohydrate}'''
        day_meal_diary_str += f'\n<b>Всего КБЖУ</b>: {int(round(total_calories, 0))}/{round(total_protein, 0)}/{round(total_fat, 0)}/{round(total_carbohydrate, 0)}'
        day_meal_diary_str += f'\n\nЕсли хотите удалить продукт - нажмите на соответствующую команду или /back, чтобы вернуться к выбору дня'
        bot.send_message(message.chat.id, day_meal_diary_str, parse_mode='HTML')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(message, food_id_handler, food_ids, period_date)
    else:
        bot.send_message(message.chat.id, f'Дневник питания за {period_date} пуст')
        process_meal_diary(message)

@cancel_on_message_confusion
def food_id_handler(message:Message, food_ids, period_date):
    if message.text:
        food_id_to_delete = str(message.text).replace('/', '')
        if food_id_to_delete == 'back':
            process_meal_diary(message)
            return
        elif food_id_to_delete.isdigit():
            food_id_to_delete = int(food_id_to_delete)
            if food_id_to_delete in food_ids:
                db.delete_food_diary_entry(food_id_to_delete)
                bot.send_message(message.chat.id, 'Продукт удален')
                print_period_foods(message, period_date)
                return
            else:
                bot.send_message(message.chat.id, 'Ошибка. ID не существует:')
        else:
            bot.send_message(message.chat.id, 'Ошибка. ID должен быть числом:')
    else:
        bot.send_message(message.chat.id, 'Ошибка. Введите ID продукта:')

    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(message, food_id_handler, food_ids, period_date)