from telebot.types import Message
from config import bot
import dbconnection as db
from meal_diary_utils import UserMealDiaryProduct
from typing import List
from nutritionix_utils import NutritionixNutrient
import nutrient_table_manager

def process_nutrient_report_creating(message:Message):
    bot.send_message(message.chat.id, 'Сейчас пришлю отчет о витаминах, минералах и других нутриентах за последние 7 дней')
    send_nutrients_report(message)

def send_nutrients_report(message:Message):
    nutrients_dict = get_nutrients_data(message)
    nutrients_data:List[NutritionixNutrient] = [db.get_nutritionix_nutrient_info(attr_id, value) for attr_id, value in nutrients_dict.items()]
    if table_file_path := nutrient_table_manager.generate_table(nutrients_data):
        with open(table_file_path, 'rb') as f:
            bot.send_chat_action(message.chat.id, action='upload_document')
            bot.send_document(message.chat.id, f)
        nutrient_table_manager.delete_table(table_file_path)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Не удалось сформировать таблицу с нутриентами')

def get_nutrients_data(message:Message):
    user_id = db.get_user_id(message.chat.id)
    meal_diary_periods = list(set(db.get_user_meal_diary_periods(user_id)))
    last_7_meal_diary_periods = meal_diary_periods[-7:]
    products_lists = [db.get_user_meal_period_data(user_id, period) for period in last_7_meal_diary_periods]
    products:List[UserMealDiaryProduct] = []
    for product in products_lists:
        products.extend(product)
    total_full_nutrients = ''.join(product.full_nutrients if product.full_nutrients is not None else '' for product in products)
    nutrients_dict = parse_full_nutrients(total_full_nutrients)
    return nutrients_dict

def parse_full_nutrients(full_nutrients_str):
    full_nutrients_str = str(full_nutrients_str).strip(',')
    nutrients_data_list = full_nutrients_str.split(',')
    nutrients_dict = {}
    for nutrient_str in nutrients_data_list:
        attr_id, nutrient_value = nutrient_str.split(':')
        nutrient_value = float(nutrient_value)
        if attr_id in nutrients_dict:
            total_nutrient_value = float(nutrients_dict[attr_id])
            nutrients_dict[attr_id] = total_nutrient_value + nutrient_value
        else:
            nutrients_dict[attr_id] = nutrient_value
    return nutrients_dict



if __name__ == '__main__':
    x = [1, 2, 3, 4, 5]
    print(x[-3:])
