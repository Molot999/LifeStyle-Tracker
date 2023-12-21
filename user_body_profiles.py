from telebot.types import Message
from config import bot
import keyboards
import dbconnection as db
from contexts import get_user_context, get_body_profile_filling_context, clear_body_profile_filling_context, UserContext, BodyProfileFillingContext
from user_body_profile_classes import UserBodyProfile, UserBodyProfileField, PhysicalActivityLevel
import user_body_profile_utils
import user_body_calculations
import utils
from user_diet_macros_utils import UserDietMacros
from decorators import cancel_on_message_confusion
from user_weight_diaries_utils import UserWeightDiaryEntry
from typing import List

activity_dict = {
    "SEDENTARY": "Минимальная физическая активность, офисная работа",
    "LIGHTLY_ACTIVE": "Легкие прогулки, ненапряжные домашние дела",
    "MODERATELY_ACTIVE": "Умеренные тренировки или физическая работа 3-4 раза в неделю",
    "VERY_ACTIVE": "Ежедневная активность, спорт или тренировки 5-6 раз в неделю",
    "EXTRA_ACTIVE": "Интенсивные тренировки, физически тяжелая работа или профессиональный спорт"
}

fitness_goals_dict = {
    "LOSS_WEIGHT": "Похудеть",
    "BUILD_MUSCLE": "Набрать мышцы",
    "MUSCLE_STRENGTH": "Увеличить силу мышц",
    "KEEP_WEIGHT": "Поддержать вес на одном уровне"
}

sex_dict = {'male':'Мужчина',
    'female':'Женщина'}

def send_user_body_profile_filling_request(message:Message):
    bot.send_message(message.chat.id,
                    """Хотите заполнить профиль физических данных (пол, возраст, вес и т.д)?\nЭти данные помогут нам для создания рекомендаций по тренировкам и питанию""",
                    reply_markup=keyboards.user_body_profile_filling_request())

def check_user_body_profile_filling_status(message:Message):
    user_id = db.get_user_id(message.chat.id)
    user_body_profile:UserBodyProfile = db.get_user_body_profile(user_id)
    if not user_body_profile:
        body_profile_filling_context:BodyProfileFillingContext = get_body_profile_filling_context(message)
        body_profile_filling_context.user_body_profile = UserBodyProfile()
        send_user_body_profile_filling_request(message)
    else:
        print_user_body_profile_info(message)

def send_body_profile_field_message(message:Message, field_type:UserBodyProfileField):
    if field_type is UserBodyProfileField.sex:
        text = 'Выберите свой пол:\n/male - Мужчина\n/female - Женщина'
    elif field_type is UserBodyProfileField.birth_date:
        text = 'Введите дату рождения в формате ДД.ММ.ГГГГ:'
    elif field_type is UserBodyProfileField.height:
        text = 'Укажите свой рост:'
    elif field_type is UserBodyProfileField.weight:
        text = 'Укажите начальный вес:'
    elif field_type is UserBodyProfileField.physical_activity_level:
        text = '\n'.join(f'/{activity_command} - {activity_text}' for activity_command, activity_text in activity_dict.items())
    elif field_type is UserBodyProfileField.goal:
        text = '\n'.join(f'/{goal_command} - {goal_text}' for goal_command, goal_text in fitness_goals_dict.items())
    else:
        print('Ошибка! send_body_profile_field_message - поля нет')
    
    bot.send_message(message.chat.id, text, parse_mode='HTML')
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(message, body_profile_field_handler, field_type)

def process_user_body_profile_filling(message:Message, to_clear_body_profile_filling_context=False):
    if to_clear_body_profile_filling_context:
        clear_body_profile_filling_context(message)
    body_profile_filling_context:BodyProfileFillingContext = get_body_profile_filling_context(message)
    user_body_profile:UserBodyProfile = body_profile_filling_context.user_body_profile
    if not user_body_profile.sex:
        unfilled_field_type = UserBodyProfileField.sex
    elif not user_body_profile.birth_date:
        unfilled_field_type = UserBodyProfileField.birth_date
    elif not user_body_profile.height:
        unfilled_field_type = UserBodyProfileField.height
    elif not user_body_profile.weight:
        unfilled_field_type = UserBodyProfileField.weight
    elif not user_body_profile.physical_activity_level:
        unfilled_field_type = UserBodyProfileField.physical_activity_level
    elif not user_body_profile.goal:
        unfilled_field_type = UserBodyProfileField.goal
    else:
        user_id = db.get_user_id(message.chat.id)
        user_body_profile.user_id = user_id

        weight_diary_entries = db.get_user_weight_diary(user_id)
        if weight_diary_entries and len(weight_diary_entries) > 0:
            weight = weight_diary_entries[0].weight
        else:
            weight = user_body_profile.weight

        bmi = user_body_calculations.calculate_bmi(weight, user_body_profile.height/100)
        user_body_profile.BMI = bmi

        user_age = utils.calculate_age(user_body_profile.birth_date)

        bmr = user_body_calculations.calculate_bmr_mifflin(weight, user_body_profile.height, user_age, user_body_profile.sex)
        user_body_profile.BMR = bmr

        physical_activity_level_index:PhysicalActivityLevel = getattr(PhysicalActivityLevel, user_body_profile.physical_activity_level).value

        tdee = user_body_calculations.calculate_tdee(bmr, physical_activity_level_index)
        user_body_profile.TDEE = tdee

        if not db.check_user_body_profile_exists(user_id):
            db.add_user_body_profile(user_body_profile)
            msg_text = 'Профиль заполнен ✅ Теперь буду учитывать эти данные в тренировках и питании\nСейчас выведу данные, которые я рассчитал, и некоторые рекомендации'
        else:
            msg_text = 'Профиль обновлен ✅'
            db.update_user_body_profile(user_id=user_id,
                                    birth_date=user_body_profile.birth_date,
                                    height=user_body_profile.height,
                                    weight=user_body_profile.weight,
                                    sex=user_body_profile.sex,
                                    physical_activity_level=user_body_profile.physical_activity_level,
                                    BMI=user_body_profile.BMI,
                                    BMR=user_body_profile.BMR,
                                    TDEE=user_body_profile.TDEE,
                                    goal=user_body_profile.goal)
            
        cals_min, cals_max = user_body_calculations.calculate_calorie_range(tdee, user_body_profile.goal)
        if not db.check_user_diet_macros_exists(user_id):
            db.set_user_diet_macros(user_id, calories_range=f'{cals_min}-{cals_max}')
        else:
            msg_text = 'Теперь вам будет необходимо установить новые цели по БЖУ в разделе "Питание - Настройки"'
            db.update_user_diet_macros(user_id=user_id,
                                    calories_range=f'{cals_min}-{cals_max}',
                                    protein_g='',
                                    fat_g='',
                                    carbohydrate_g='')

        bot.send_message(message.chat.id, msg_text)
        print_user_body_profile_info(message)
        return

    send_body_profile_field_message(message, unfilled_field_type)

@cancel_on_message_confusion
def body_profile_field_handler(message:Message, field_type:UserBodyProfileField):
    if field_value := message.text:
        body_profile_filling_context:BodyProfileFillingContext = get_body_profile_filling_context(message)
        user_body_profile:UserBodyProfile = body_profile_filling_context.user_body_profile
        if field_type is UserBodyProfileField.sex:
            sex = str(field_value).replace('/', '')
            if sex in sex_dict:
                user_body_profile.sex = sex
            else:
                bot.send_message(message.chat.id, 'Ошибка. Нажмите на соответствующую команду:')
                bot.clear_step_handler_by_chat_id(message.chat.id)
                bot.register_next_step_handler(message, body_profile_field_handler, field_type)
                return
            
        elif field_type is UserBodyProfileField.birth_date:
            birth_date = str(field_value)
            if user_body_profile_utils.is_valid_birth_date(birth_date):
                user_body_profile.birth_date = birth_date
            else:
                bot.send_message(message.chat.id, 'Ошибка. Введите дату рождения в формате ДД.ММ.ГГГ (например: 18.02.2000):')
                bot.clear_step_handler_by_chat_id(message.chat.id)
                bot.register_next_step_handler(message, body_profile_field_handler, field_type)
                return
            
        elif field_type is UserBodyProfileField.height:
            height = str(field_value)
            if height.isdigit() and user_body_profile_utils.is_non_negative_number(height):
                user_body_profile.height = int(height)
            else:
                bot.send_message(message.chat.id, 'Ошибка. Введите рост в сантиметрах (например: 173):')
                bot.clear_step_handler_by_chat_id(message.chat.id)
                bot.register_next_step_handler(message, body_profile_field_handler, field_type)
                return
            
        elif field_type is UserBodyProfileField.weight:
            weight = str(field_value).replace(',', '.')
            if user_body_profile_utils.is_valid_number(weight) and user_body_profile_utils.is_non_negative_number(weight):
                user_body_profile.weight = float(weight)
            else:
                bot.send_message(message.chat.id, 'Ошибка. Введите вес в килограммах (например: 95 или 105.5):')
                bot.clear_step_handler_by_chat_id(message.chat.id)
                bot.register_next_step_handler(message, body_profile_field_handler, field_type)
                return
            
        elif field_type is UserBodyProfileField.physical_activity_level:
            physical_activity_level = str(field_value).replace('/', '')
            if physical_activity_level in activity_dict:
                user_body_profile.physical_activity_level = physical_activity_level
            else:
                bot.send_message(message.chat.id, 'Ошибка. Нажмите на соответствующую команду:')
                bot.clear_step_handler_by_chat_id(message.chat.id)
                bot.register_next_step_handler(message, body_profile_field_handler, field_type)
                return
            
        elif field_type is UserBodyProfileField.goal:   
            goal = str(field_value).replace('/', '')
            if goal in fitness_goals_dict:
                user_body_profile.goal = goal
            else:
                bot.send_message(message.chat.id, 'Ошибка. Нажмите на соответствующую команду:')
                bot.clear_step_handler_by_chat_id(message.chat.id)
                bot.register_next_step_handler(message, body_profile_field_handler, field_type)
                return
        else:
            print('Ошибка! body_profile_field_handler - поля нет')

        process_user_body_profile_filling(message)

    else:
        bot.send_message(message.chat.id, 'Ошибка. Введите значение:')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(message, body_profile_field_handler, field_type)

def print_user_body_profile_info(message:Message):
    user_id = db.get_user_id(message.chat.id)
    user_body_profile = db.get_user_body_profile(user_id)
    if user_weight_diary_entries := db.get_user_weight_diary(user_id):
        last_weight_diary_entry:UserWeightDiaryEntry = user_weight_diary_entries[-1]
        last_weight = last_weight_diary_entry.weight
    else:
        last_weight = None
    age = utils.calculate_age(user_body_profile.birth_date)
    bmi = user_body_profile.BMI
    bmr = user_body_profile.BMR
    tdee = user_body_profile.TDEE
    goal = user_body_profile.goal
    msg = f'''
Пол: {sex_dict.get(user_body_profile.sex)}
Возраст: {age}
Рост: {user_body_profile.height}
Вес (начальный): {user_body_profile.weight}
Вес (текущий): {last_weight or user_body_profile.weight}
ИМТ: {bmi}
Физическая активность: {activity_dict.get(user_body_profile.physical_activity_level)}
Цель: {fitness_goals_dict.get(goal)}
Базовый обмен веществ: {bmr} ккал
Суточные энергозатраты: {tdee} ккал'''
    user_diet_macros:UserDietMacros = db.get_user_diet_macros(user_id)
    cals_min, cals_max = str(user_diet_macros.calories_range).split('-')
    if goal == 'LOSS_WEIGHT':
        goal_msg = f'\nДля похудения вам необходимо потреблять от <b>{cals_min}</b> до <b>{cals_max}</b> ккал в сутки'
    elif goal == 'BUILD_MUSCLE':
        goal_msg = f'\nДля наращивания мышц вам необходимо потреблять от <b>{cals_min}</b> до <b>{cals_max}</b> ккал в сутки'
    elif goal == 'MUSCLE_STRENGHT':
        goal_msg = f'\nДля увеличения силы мышц вам необходимо потреблять от <b>{cals_min}</b> до <b>{cals_max}</b> ккал в сутки'
    elif goal == 'KEEP_WEIGHT':
        goal_msg = f'\nДля поддержания веса вам необходимо потреблять <b>{int(round(tdee, 0))}</b> ккал в сутки'
    else:
        goal_msg = ''

    msg += goal_msg
    bot.send_message(message.chat.id, msg, parse_mode='HTML', reply_markup=keyboards.user_body_profile_info_keyboard())

def update_user_body_profile(message:Message, new_weight):
    try:
        new_weight = float(new_weight)
        user_id = db.get_user_id(message.chat.id)
        user_body_profile:UserBodyProfile = db.get_user_body_profile(user_id)

        bmi = user_body_calculations.calculate_bmi(new_weight, user_body_profile.height/100)
        user_body_profile.BMI = bmi

        user_age = utils.calculate_age(user_body_profile.birth_date)

        bmr = user_body_calculations.calculate_bmr_mifflin(new_weight, user_body_profile.height, user_age, user_body_profile.sex)
        user_body_profile.BMR = bmr

        physical_activity_level_index:PhysicalActivityLevel = getattr(PhysicalActivityLevel, user_body_profile.physical_activity_level).value

        tdee = user_body_calculations.calculate_tdee(bmr, physical_activity_level_index)
        user_body_profile.TDEE = tdee

        db.update_user_body_profile(user_id=user_id,
                                    BMI=user_body_profile.BMI,
                                    BMR=user_body_profile.BMR,
                                    TDEE=user_body_profile.TDEE
                                    )
    except Exception as e:
        print('Ошибка! update_user_body_profile():', e)