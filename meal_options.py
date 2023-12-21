from config import bot
from telebot.types import Message
import dbconnection as db
from contexts import get_user_context, UserContext
from user_diet_macros_utils import UserDietMacros
import user_diet_macros
import user_body_profiles
import keyboards
from subscriptions_manager import check_subscription


def process_meal_options(message:Message):
    user_id = db.get_user_id(message.chat.id)
    if user_body_profile := db.get_user_body_profile(user_id):
        if db.check_is_user_diet_macros_filled(user_id):
            user_diet_macros_data = db.get_user_diet_macros(user_id)
            calories_min, calories_max = str(user_diet_macros_data.calories_range).split('-')
            user_diet_macros_str = f'''
Цели вашей диеты на данный момент:
<b>Калории</b>: от {calories_min} до {calories_max}
<b>Белки</b>: {user_diet_macros_data.protein_g} г
<b>Жиры</b>: {user_diet_macros_data.fat_g} г
<b>Углеводы</b>: {user_diet_macros_data.carbohydrate_g} г
'''
            bot.send_message(message.chat.id, user_diet_macros_str, parse_mode='HTML', reply_markup=keyboards.meal_options_keyboard())
        else:
            bot.send_message(message.chat.id, 'Чтобы эффективно отслеживать свое питание вам следует установить цели по калориям, белкам, жирам и углеводам. ')
            user_diet_macros.process_input_diet_macros(message, user_body_profile)
    else:
        #bot.send_message(message.chat.id, 'Для получения рекоммендаций по питанию и тренировкам вам следует заполнить профиль физических данных (пол, возраст, вес и т.д)')
        user_body_profiles.send_user_body_profile_filling_request(message)

@check_subscription
def edit_meal_options(message:Message):
    user_id = db.get_user_id(message.chat.id)
    user_body_profile = db.get_user_body_profile(user_id)
    user_diet_macros.process_input_diet_macros(message, user_body_profile)