import dbconnection as db
from config import bot
from telebot.types import Message
import keyboards
from receipts_utils import Receipt, ReceiptIngredient, ReceiptStep
from typing import List
from decorators import cancel_on_message_confusion
import receipt_searcher
from user_body_profile_utils import is_valid_number
from informer import isend
import keyboards
from user_foods_utils import UserFood, correct_user_foods_text_len
from user_body_profile_utils import is_valid_number
import datetime
from contexts import get_input_user_foods_to_diary_context, InputUserFoodToDiaryContext
from subscriptions_manager import check_subscription

main_nutrients_map = {
    1: '✅',
    0: '❔',
    None: '❌'
}

def process_user_foods(message:Message):
    bot.send_message(message.chat.id,
                    'Здесь вы можете добавлять продукты питания, которые занесли самостоятельно, а также редактировать список данных продуктов',
                    reply_markup=keyboards.user_foods_keyboard())
@check_subscription
def search_user_food(message:Message):
    user_id = db.get_user_id(message.chat.id)
    if db.is_user_foods_added(user_id):
        msg = bot.send_message(message.chat.id, 'Введите название продукта для поиска:')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(msg, user_foods_title_handler)
    else:
        bot.send_message(message.chat.id, 'Вы еще не добавляли свои продукты')

@cancel_on_message_confusion
def user_foods_title_handler(message:Message):
    if query := message.text:
        user_id = db.get_user_id(message.chat.id)
        if found_foods := db.search_user_foods(user_id, query):
            if len(found_foods) > 1:
                print_found_user_foods(message, found_foods)
            else:
                send_user_food_info(message, found_foods[0], found_foods)
            return
        else:
            msg = bot.send_message(message.chat.id, 'Подходящих результатов не найдено. Попробуйте еще раз:')
    else:
        msg = bot.send_message(message.chat.id, 'Ошибка. Введите название продукта для поиска:')

    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(msg, user_foods_title_handler)

def print_found_user_foods(message:Message, found_foods:List[UserFood]):
    found_foods_text = 'Для выбора нажмите на команду слева от названия:'
    found_foods_list_text = ''
    for food in found_foods:
        found_foods_list_text += f'\n/{food.id} {food.title}'
    result_text = correct_user_foods_text_len(found_foods_list_text, len(found_foods_text))
    found_foods_text += result_text
    msg = bot.send_message(message.chat.id, found_foods_text, parse_mode='HTML')
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(msg, user_food_id_handler, found_foods)

@cancel_on_message_confusion
def user_food_id_handler(message:Message, found_foods:List[UserFood]):
    if message.text:
        food_id = str(message.text).replace('/', '')
        if food_id.isdigit():
            if selected_food_list := [food for food in found_foods if str(food.id) == food_id]:
                selected_food:UserFood = selected_food_list[0]
                send_user_food_info(message, selected_food, found_foods)
                return
            else:
                msg = bot.send_message(message.chat.id, 'Продукт не найден. Попробуйте еще раз')
        else:
            msg = bot.send_message(message.chat.id, 'Неверная команда. Попробуйте еще раз')
    else:
        msg = bot.send_message(message.chat.id, 'Нажмите на команду слева, чтобы выбрать продукт')

    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(msg, user_food_id_handler, found_foods)

def send_user_food_info(message:Message, food:UserFood, found_foods:List[UserFood]):
    food_weight = food.weight or 100
    calories_100g = (food.calories*100)/food_weight
    protein_100g = (food.protein*100)/food_weight
    fat_100g = (food.fat*100)/food_weight
    carbohydrate_100g = (food.carbohydrate*100)/food_weight
    is_animal_proteins = main_nutrients_map.get(food.is_animal_protein) or '-'
    is_unsaturated_fats = main_nutrients_map.get(food.is_unsaturated_fats) or '-'
    is_complex_carbohydrates = main_nutrients_map.get(food.is_complex_carbohydrates) or '-'
    one_piece_weight = food.one_piece_weight or 'не установлено'
    user_food_info_text = f'''
<b>{food.title}</b>
Вес 1 шт: {one_piece_weight}
Категория: {food.group_name}
Животный белок: {is_animal_proteins}
Ненасыщенные жиры: {is_unsaturated_fats}
Сложные углеводы: {is_complex_carbohydrates}
<u>Пищевая ценность</u> (100 г)
Калории: {calories_100g}
Белки: {protein_100g}
Жиры: {fat_100g}
Углеводы: {carbohydrate_100g}

Чтобы выбрать другой продукт - нажмите на его команду'''
    
    input_user_foods_to_diary_context:InputUserFoodToDiaryContext = get_input_user_foods_to_diary_context(message)
    input_user_foods_to_diary_context.clear()
    input_user_foods_to_diary_context.food = food
    input_user_foods_to_diary_context.calories_100g = calories_100g
    input_user_foods_to_diary_context.protein_100g = protein_100g
    input_user_foods_to_diary_context.fat_100g = fat_100g
    input_user_foods_to_diary_context.carbohydrate_100g = carbohydrate_100g
    
    msg = bot.send_message(message.chat.id, user_food_info_text, parse_mode='HTML', reply_markup=keyboards.user_food_info_keyboard())
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(msg, user_food_id_handler, found_foods)

def process_adding_user_food_to_meal_diary(message:Message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    msg = bot.send_message(message.chat.id, 'Введите вес продукта в граммах, после чего он будет добавлен в дневник питания:')
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(msg, user_food_weight_handler)

@cancel_on_message_confusion
def user_food_weight_handler(message:Message):
    if weight_text := message.text:
        weight = weight_text.replace(',', '.')
        if is_valid_number(weight):
            add_user_food_to_diary(message, float(weight))
            return
        else:
            msg = bot.send_message(message.chat.id, 'Ошибка. Введите неотрицательное число:')
    else:
        msg = bot.send_message(message.chat.id, 'Ошибка. Введите количество продукта в граммах:')

    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(msg, user_food_weight_handler)

def add_user_food_to_diary(message:Message, weight:float):
    input_user_foods_to_diary_context:InputUserFoodToDiaryContext = get_input_user_foods_to_diary_context(message)
    food:UserFood = input_user_foods_to_diary_context.food
    calories_100g = input_user_foods_to_diary_context.calories_100g
    protein_100g = input_user_foods_to_diary_context.protein_100g
    fat_100g = input_user_foods_to_diary_context.fat_100g
    carbohydrate_100g = input_user_foods_to_diary_context.carbohydrate_100g

    user_id = db.get_user_id(message.chat.id)
    current_datetime = datetime.datetime.now()
    current_datetime_string = current_datetime.strftime("%Y.%m.%d %H:%M")
    db.add_food_diary_entry(
        user_id=user_id,
        food_name=food.title,
        brand_name=None,
        serving_qty=None,
        serving_weight_grams=weight,
        calories=calories_100g*(weight/100),
        total_fat=fat_100g*(weight/100),
        saturated_fat=None,
        cholesterol=None,
        total_carbohydrate=carbohydrate_100g*(weight/100),
        dietary_fiber=None,
        sugars=None,
        protein=protein_100g*(weight/100),
        potassium=None,
        p=None,
        full_nutrients = None,
        datetime=current_datetime_string
    )
    bot.send_message(message.chat.id, 'Продукт добавлен ✅')
    process_user_foods(message)