from telebot import types
import dbconnection as db
from subscriptions_utils import AvailableSubscription
from typing import List

def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    nutrition = types.KeyboardButton('🍽️Питание')
    training = types.KeyboardButton('💪Тренировки')
    profile = types.KeyboardButton('👤Профиль')
    calcs = types.KeyboardButton('🔢Калькуляторы')
    support = types.KeyboardButton('💬Поддержка')
    keyboard.add(nutrition, training, profile, calcs, support)
    return keyboard

def offer_subscription(available_subscriptions:List[AvailableSubscription]):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Тестовый период (для новых пользователей)', callback_data='subscription#test'))
    for available_subscription in available_subscriptions:
        keyboard.add(types.InlineKeyboardButton(f'{available_subscription.period} дней - {available_subscription.price}₽', callback_data=f'subscription#{available_subscription.id}'))
    return keyboard

def support_menu():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Чат', url='https://t.me/onishch'))
    return keyboard

def pay_keyboard(url, label):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Оплатить', url=url))
    keyboard.add(types.InlineKeyboardButton('Проверить оплату', callback_data=f'check_payment#{label}'))
    return keyboard

def user_workouts(is_started_workout=False):
    keyboard = types.InlineKeyboardMarkup()
    if not is_started_workout:
        btn1 = types.InlineKeyboardButton('🏋️‍♂️ Начать новую', callback_data='new_workout')
    else:
        btn1 = types.InlineKeyboardButton('🏋️‍♂️ Продолжить', callback_data='continue_workout')
    btn2 = types.InlineKeyboardButton('📊 Статистика тренировок', callback_data='workouts_stat')
    keyboard.add(btn1, btn2)
    return keyboard

def workout_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('➕ Новое упражнение', callback_data='new_exercise')
    btn2 = types.InlineKeyboardButton('🏁 Закончить тренировку', callback_data='finish_workout')
    keyboard.add(btn1, btn2)
    return keyboard

def selected_exercise_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('▶️ Начать упражнение', callback_data='start_exercise')
    btn2 = types.InlineKeyboardButton('🔄 Другое', callback_data='other_exercise')
    keyboard.add(btn1, btn2)
    return keyboard

def started_exercise_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('➕ Новый подход', callback_data='new_exercise_set')
    btn2 = types.InlineKeyboardButton('🏁 Закончить упражнение', callback_data='finish_exercise')
    keyboard.add(btn1, btn2)
    return keyboard

def started_exercise_set_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('🏁 Закончить подход', callback_data='finish_exercise_set')
    btn2 = types.InlineKeyboardButton('❌ Отменить подход', callback_data='undo_exercise_set')
    keyboard.add(btn1, btn2)
    return keyboard

def user_body_profile_filling_request():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('✅ Да, заполнить профиль', callback_data='yes_fill_body_profile')
    btn2 = types.InlineKeyboardButton('⏱️ Позже', callback_data='no_fill_body_profile')
    keyboard.add(btn1, btn2)
    return keyboard

def user_meausurements_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('➕ Добавить замер', callback_data='add_measurement')
    keyboard.add(btn1)
    return keyboard

def nutritions_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('🍽️ Добавить прием пищи', callback_data='add_meal')
    btn2 = types.InlineKeyboardButton('🥑 Мои продукты', callback_data='user_foods')
    btn3 = types.InlineKeyboardButton('📅 Дневник питания', callback_data='meal_diary')
    btn4 = types.InlineKeyboardButton('🍲 Рецепты', callback_data='receipts')
    btn5 = types.InlineKeyboardButton('⚙️ Настройки питания', callback_data='meal_options')
    keyboard.add(btn1, btn2, btn3, btn4, btn5)
    #keyboard.add(btn1, btn2, btn3, btn4, btn5)
    return keyboard

def handled_meal_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('✅ Да', callback_data='true_handled_meal')
    btn2 = types.InlineKeyboardButton('❌ Нет', callback_data='false_handled_meal')
    keyboard.add(btn1, btn2)
    return keyboard

def diet_macros_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('✅ Подтвердить', callback_data='true_diet_macros')
    btn2 = types.InlineKeyboardButton('🔄 Изменить', callback_data='false_diet_macros')
    keyboard.add(btn1, btn2)
    return keyboard

def user_body_profile_info_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('🔄 Изменить', callback_data='edit_body_profile')
    btn2 = types.InlineKeyboardButton('📋 Дневник веса', callback_data='weight_diary')
    btn3 = types.InlineKeyboardButton('📋 Замеры', callback_data='measurements_diary')
    btn4 = types.InlineKeyboardButton('🕓 Часовой пояс', callback_data='timezone')
    btn5 = types.InlineKeyboardButton('💎 Подписка', callback_data='my_subscription')
    keyboard.add(btn1, btn2, btn3, btn4, btn5)
    return keyboard

def user_weight_diary_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('📝 Добавить запись', callback_data='add_weight_diary_entry')
    keyboard.add(btn1)
    return keyboard

def user_measurements_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('📝 Добавить запись', callback_data='add_measurement')
    keyboard.add(btn1)
    return keyboard

def meal_options_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('🔄 Изменить настройки', callback_data='edit_meal_options')
    keyboard.add(btn1)
    return keyboard

def workouts_statistics_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('📊 Общая статистика', callback_data='general_stats')
    btn2 = types.InlineKeyboardButton('📊 Статистика упражнений', callback_data='exercise_stats')
    keyboard.add(btn1, btn2)
    return keyboard

def user_body_profile_editing_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('🔄 Изменить профиль', callback_data='edit_body_profile')
    btn2 = types.InlineKeyboardButton('📋 Дневник веса', callback_data='weight_diary')
    btn3 = types.InlineKeyboardButton('📋 Дневник замеров', callback_data='measurements_diary')
    keyboard.add(btn1, btn2, btn3)
    return keyboard

def receipts_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('🔍 Найти рецепт', callback_data='search_receipt')
    btn2 = types.InlineKeyboardButton('🎲 Случайный рецепт', callback_data='random_receipt')
    keyboard.add(btn1, btn2)
    return keyboard

def random_receipt_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('🔄 Другой', callback_data='another_random_receipt')
    keyboard.add(btn1)
    return keyboard

def user_foods_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('🔍 Поиск', callback_data='search_user_foods')
    btn2 = types.InlineKeyboardButton('📝 Редактировать', callback_data='edit_user_foods')
    keyboard.add(btn1, btn2)
    return keyboard

def user_foods_editing_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('📥 Загрузить', callback_data='user_foods_upload')
    btn2 = types.InlineKeyboardButton('📤 Скачать', callback_data='user_foods_download')
    btn3 = types.InlineKeyboardButton('📄 Шаблон', callback_data='user_foods_template')
    btn4 = types.InlineKeyboardButton('🗑️ Удалить все', callback_data='process_deleting_user_foods')
    keyboard.add(btn1, btn2, btn3)
    keyboard.add(btn4)
    return keyboard

def new_user_foods_table_info_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('✅ Да', callback_data='confirm_new_user_foods')
    btn2 = types.InlineKeyboardButton('❌ Нет', callback_data='decline_new_user_foods')
    btn3 = types.InlineKeyboardButton('🔄 Другой пример', callback_data='another_new_user_foods_example')
    keyboard.add(btn1, btn2)
    keyboard.add(btn3)
    return keyboard

def user_food_info_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('➕ Добавить в дневник', callback_data='add_user_food_to_meal_diary')
    btn2 = types.InlineKeyboardButton('🔍 Искать снова', callback_data='search_user_foods')
    keyboard.add(btn1, btn2)
    return keyboard

def user_foods_delete_checking_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('🗑️ Удалить все', callback_data='delete_user_foods')
    btn2 = types.InlineKeyboardButton('❌ Отмена', callback_data='cancel_deleting_user_foods')
    keyboard.add(btn1, btn2)
    return keyboard

def meal_diary_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('📊 Отчет о питательных веществах', callback_data='nutrient_report')
    keyboard.add(btn1)
    return keyboard

def check_timezone_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('✅ Да', callback_data='yes_timezone')
    btn2 = types.InlineKeyboardButton('❌ Нет', callback_data='no_timezone')
    keyboard.add(btn1, btn2)
    return keyboard

def delete_weight_diary_entry_keyboard(user_weight_diary_entry_id):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('🗑️ Удалить', callback_data=f'delete_weight_diary_entry#{user_weight_diary_entry_id}')
    keyboard.add(btn1)
    return keyboard

def delete_body_measurements_entry_keyboard(body_measurement_id):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('🗑️ Удалить', callback_data=f'delete_body_measurements_entry#{body_measurement_id}')
    keyboard.add(btn1)
    return keyboard

def delete_workout_keyboard(workout_id):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('🗑️ Удалить', callback_data=f'delete_workout#{workout_id}')
    keyboard.add(btn1)
    return keyboard

def user_timezone_keyboard(edit:bool):
    text = 'Изменить' if edit else 'Установить'
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text, callback_data='edit_timezone')
    keyboard.add(btn1)
    return keyboard

def exercise_searching_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Назад', callback_data='continue_workout')
    keyboard.add(btn1)
    return keyboard

def exercise_list_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Назад', callback_data='new_exercise')
    keyboard.add(btn1)
    return keyboard