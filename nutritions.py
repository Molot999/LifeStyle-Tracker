from config import bot
from telebot.types import Message
import keyboards
import nutritionix
from typing import List
from nutritionix_utils import NutritionixFood
import translater
from contexts import get_food_input_context, get_user_context, FoodInputContext, UserContext
import dbconnection as db
import datetime
import yandex_cloud
from decorators import cancel_on_message_confusion
import nutrition_analyzer
import traceback
from utils import get_now_date
import file_utils
import nutritionix_cache
import time
from meal_diary_utils import UserMealDiaryProduct
from nutrition_utils import query_examples
import random
from subscriptions_manager import check_subscription

def process_nutrition(message:Message):
    user_id = db.get_user_id(message.chat.id)
    if today_meal_data := db.get_user_meal_period_data(user_id, datetime.datetime.now().strftime('%Y.%m.%d')):
        try:
            total_calories = int(sum(meal_data.calories or 0 for meal_data in today_meal_data))
            total_protein = int(sum(meal_data.protein or 0 for meal_data in today_meal_data))
            total_fat = int(sum(meal_data.total_fat or 0 for meal_data in today_meal_data))
            total_carbohydrate = int(sum(meal_data.total_carbohydrate or 0 for meal_data in today_meal_data))
            total_dietary_fiber = int(sum(meal_data.dietary_fiber or 0 for meal_data in today_meal_data))
            text = f'За сегодня калорий {total_calories}. Всего белков - {total_protein}, жиров - {total_fat}, углеводов - {total_carbohydrate}, а клетчатки - {total_dietary_fiber}'
            text += nutrition_analyzer.get_analyze_str(user_id, total_calories, total_protein, total_fat, total_carbohydrate)
        except Exception as e:
            traceback.print_exc()
            print('Ошибка! process_nutrition() -', e)
            text = 'Здесь вы можете добавить прием пищи, посмотреть свой дневник питания или настроить КБЖУ для дальнейшего отслеживания'
    else:
        text = 'Здесь вы можете добавить прием пищи, посмотреть свой дневник питания или настроить КБЖУ для дальнейшего отслеживания'
    
    bot.send_message(message.chat.id,text,reply_markup=keyboards.nutritions_keyboard())

@check_subscription
def add_meal(message:Message):
    bot.send_message(message.chat.id,
                    f'Введите съеденные продукты (например: {str(random.choice(query_examples)).lower()}) или перечислите их в голосовом сообщении:')
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(message, meal_handler)

@cancel_on_message_confusion
def meal_handler(message:Message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.content_type == 'text':
        # Если введен штрихкод
        # if str(message.text).isdigit():
        #     handle_barcode(message, False)
        #     return
        parse_food(message, message.text)
    # elif message.content_type == 'photo':
    #     handle_barcode(message, True)
    elif message.content_type == 'voice':
        saved_file_path = file_utils.save_audiomessage(message)
        if saved_file_path:
            meal_text = yandex_cloud.get_text_from_speech(saved_file_path)
            if meal_text:
                bot.send_message(message.chat.id, f'Окэй, ищем <b>{meal_text}</b>', parse_mode='HTML')
                file_utils.delete_file(saved_file_path)
                parse_food(message, meal_text)
                return
        bot.send_message(message.chat.id, 'Ошибка в распознавании аудиосообщения. Попробуйте еще раз:')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(message, meal_handler)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Попробуйте еще раз:')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(message, meal_handler)

def parse_food(message, meal_text):  # sourcery skip: extract-method
    food_input_context:FoodInputContext = get_food_input_context(message)
    cache_found, foods = nutritionix_cache.search_query_response(meal_text)
    if not cache_found:
        eng_meal_text = translater.translate_from_rus_to_eng(meal_text)
        foods, data = nutritionix.get_foods_list(eng_meal_text)
    if foods:
        if len(foods) == 1:
            food = foods[0]
            bot.send_photo(message.chat.id, food.photo_url)
        food_input_context.foods = foods
        foods_msg = ''
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbohydrate = 0
        for food in foods:
            food_name = str(translater.translate_from_eng_to_rus(food.food_name)).title()
            calories = float(food.nf_calories)
            total_calories += calories
            protein = float(food.nf_protein)
            total_protein += protein
            fat = float(food.nf_total_fat)
            total_fat += fat
            carbohydrate = float(food.nf_total_carbohydrate)
            total_carbohydrate += carbohydrate
            foods_msg += f'''<b>{food_name}</b> {food.serving_weight_grams} г / {int(calories)} ккал
БЖУ: {protein}/{fat}/{carbohydrate}
'''     
        foods_msg += f'\nВсего КБЖУ: {int(total_calories)}/{int(total_protein)}/{int(total_fat)}/{int(total_carbohydrate)}'
        foods_msg += '\nВсе верно?'
        bot.send_message(message.chat.id, foods_msg, parse_mode='HTML', reply_markup=keyboards.handled_meal_keyboard())
    else:
        bot.send_message(message.chat.id, 'Не удалось распознать, попробуйте еще раз:')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(message, meal_handler)

    if not cache_found:
        nutritionix_cache.save_to_cache(meal_text, data, get_now_date())

# @cancel_on_message_confusion
# def handle_barcode(message:Message, is_photo):
#     if is_photo:
#         barcode_text = barcode_reader.handle_barcode_image(message)
#         #bot.send_message(message.chat.id, '*Тест*')
#     else:
#         barcode_text = message.text

#     if product := barcode_searcher.get_product(barcode_text):
#         bot.send_message(message.chat.id,
# f'''
# {product.name}
# Бренд: {product.brand_name or ''}
# Калорийность (100 г): {product.calories_100_g or ''}
# Белки: {product.protein_g or ''}
# Жиры: {product.fat_g or ''}
# Насыщенные жиры: {product.saturated_fat_g or ''}
# Углеводы: {product.carbohydrate_g or ''}
# Сахар: {product.sugar_g or ''}
# Клетчатка: {product.cellulose_g or ''}
# Соль: {product.salt_g or ''}

# ''')
#     else:
#         bot.send_message(message.chat.id, 'Штрихкод не найден. Попробуйте еще раз:')
#         bot.clear_step_handler_by_chat_id(message.chat.id)
#         bot.register_next_step_handler(message, meal_handler)

def add_food_diary_entry(message):
    food_input_context:FoodInputContext = get_food_input_context(message)
    foods:List[NutritionixFood] = food_input_context.foods
    if not foods:
        bot.send_message(message.chat.id, 'Произошла ошибка, нажмите /start и продолжите')
        return
    user_id = db.get_user_id(message.chat.id)
    if not user_id:
        bot.send_message(message.chat.id, 'Пользователь не найден, нажмите /start и продолжите')
        return
    current_datetime = datetime.datetime.now()
    current_datetime_string = current_datetime.strftime("%Y.%m.%d %H:%M")
    for food in foods:
        full_nutrients_str = ''
        for nutrient in food.full_nutrients:
            if nutrient.value not in [0, '0']:
                full_nutrients_str += f',{nutrient.attr_id}:{nutrient.value}'
        full_nutrients_str.strip(',')
        db.add_food_diary_entry(
            user_id=user_id,
            food_name=str(translater.translate_from_eng_to_rus(food.food_name)).title(),
            brand_name=food.brand_name,
            serving_qty=food.serving_qty,
            serving_weight_grams=food.serving_weight_grams,
            calories=food.nf_calories,
            total_fat=food.nf_total_fat,
            saturated_fat=food.nf_saturated_fat,
            cholesterol=food.nf_cholesterol,
            total_carbohydrate=food.nf_total_carbohydrate,
            dietary_fiber=food.nf_dietary_fiber,
            sugars=food.nf_sugars,
            protein=food.nf_protein,
            potassium=food.nf_potassium,
            p=food.nf_p,
            full_nutrients = full_nutrients_str,
            datetime=current_datetime_string
        )
    bot.send_message(message.chat.id, 'Дневник питания обновлен')
    process_nutrition(message)