from config import bot
from telebot.types import Message
from contexts import get_input_diet_macros_context, get_user_context, InputDietMacrosContext, UserContext
from user_body_profile_classes import UserBodyProfile
import user_diet_macros_utils
import dbconnection as db
from user_diet_macros_utils import UserDietMacros, NUTRIENT_CALORIES
import keyboards
from decorators import cancel_on_message_confusion
from informer import isend
from user_body_profile_utils import is_valid_number
import nutritions

def process_input_diet_macros(message:Message, user_body_profile:UserBodyProfile):
    isend(username=message.from_user.username, chat_id=message.chat.id, func_name='process_input_diet_macros')
    process_protein_calculating(message, user_body_profile)

def process_protein_calculating(message, user_body_profile:UserBodyProfile):
    isend(username=message.from_user.username, chat_id=message.chat.id, func_name='process_protein_calculating')
    user_weight = user_body_profile.weight
    daily_protein_requirement_1kg = user_diet_macros_utils.calculate_protein_requirement(user_body_profile.physical_activity_level, user_body_profile.goal)
    daily_protein_requirement = round(daily_protein_requirement_1kg * user_weight)
    msg = bot.send_message(message.chat.id,
f'''
В соответствии с вашей целью и уровнем физической активности дневная потребность в белках составляет примерно {daily_protein_requirement} грамм.
Нажмите на /{daily_protein_requirement} чтобы применить данную норму или введите другое значение:
''')
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(msg, protein_requirement_handler, user_body_profile)

def process_fat_calculating(message, user_body_profile:UserBodyProfile):
    isend(username=message.from_user.username, chat_id=message.chat.id, func_name='process_fat_calculating')
    user_weight = user_body_profile.weight
    daily_fat_requirement_1kg = user_diet_macros_utils.calculate_fat_requirement(user_body_profile.physical_activity_level)
    daily_fat_requirement = round(daily_fat_requirement_1kg * user_weight)
    msg = bot.send_message(message.chat.id,
f'''
По расчетам ваша потребность в жирах составляет около {daily_fat_requirement} грамм.
Нажмите на /{daily_fat_requirement} чтобы применить данную норму или введите другое значение:
''')
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(msg, fat_requirement_handler, user_body_profile)

def process_carbohydrate_calculating(message, user_body_profile:UserBodyProfile):
    isend(username=message.from_user.username, chat_id=message.chat.id, func_name='process_carbohydrate_calculating')
    user_id = db.get_user_id(message.chat.id)
    user_diet_macros:UserDietMacros = db.get_user_diet_macros(user_id)
    calories_range = user_diet_macros.calories_range
    min_cals, max_cals = str(calories_range).split('-')
    min_cals = int(min_cals)
    max_cals = int(max_cals)
    input_diet_macros_context:InputDietMacrosContext = get_input_diet_macros_context(message)
    protein_requirement = input_diet_macros_context.protein
    protein_requirement_cals = protein_requirement*NUTRIENT_CALORIES['protein']
    print('protein_requirement_cals', protein_requirement_cals)
    fat_requirement = input_diet_macros_context.fat
    fat_requirement_cals = fat_requirement*NUTRIENT_CALORIES['fat']
    print('fat_requirement_cals', fat_requirement_cals)
    protein_fat_cals = protein_requirement_cals + fat_requirement_cals
    print('protein_fat_cals', protein_fat_cals)
    min_cals_balance = min_cals - protein_fat_cals
    print('min_cals_balance', min_cals_balance)
    max_cals_balance = max_cals - protein_fat_cals
    print('max_cals_balance', max_cals_balance)
    min_carbohydrate = min_cals_balance/NUTRIENT_CALORIES['carbohydrate']
    max_carbohydrate = max_cals_balance/NUTRIENT_CALORIES['carbohydrate']
    print('carbohydrate min/max', min_carbohydrate, max_carbohydrate)
    average_carbohydrate = round((max_carbohydrate+min_carbohydrate)/2)
    msg = bot.send_message(message.chat.id,
f'''
Что касается углеводов, то для вас норма составляет около {average_carbohydrate} грамм.
Нажмите на /{average_carbohydrate} чтобы применить данную норму или введите другое значение:
''')
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(msg, carbohydrate_requirement_handler, user_diet_macros)

@cancel_on_message_confusion
def protein_requirement_handler(message:Message, user_body_profile:UserBodyProfile):
    isend(username=message.from_user.username, chat_id=message.chat.id, func_name='protein_requirement_handler', inputted_value=message.text)
    protein_requirement = message.text
    if protein_requirement and is_valid_number(protein_requirement.replace('/', '')):
        protein_requirement = protein_requirement.replace('/', '')
        input_diet_macros_context:InputDietMacrosContext = get_input_diet_macros_context(message)
        input_diet_macros_context.protein = int(protein_requirement)
        process_fat_calculating(message, user_body_profile)
    else:
        msg = bot.send_message(message.chat.id, 'Введите значение или нажмите на команду для применения рассчитанного значения')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(msg, protein_requirement_handler, user_body_profile)

@cancel_on_message_confusion
def fat_requirement_handler(message:Message, user_body_profile:UserBodyProfile):
    isend(username=message.from_user.username, chat_id=message.chat.id, func_name='fat_requirement_handler', inputted_value=message.text)
    fat_requirement = message.text
    if fat_requirement and is_valid_number(fat_requirement.replace('/', '')):
        fat_requirement = fat_requirement.replace('/', '')
        input_diet_macros_context:InputDietMacrosContext = get_input_diet_macros_context(message)
        input_diet_macros_context.fat = int(fat_requirement)
        process_carbohydrate_calculating(message, user_body_profile)
    else:
        msg = bot.send_message(message.chat.id, 'Введите значение или нажмите на команду для применения рассчитанного значения')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(msg, fat_requirement_handler, user_body_profile)

@cancel_on_message_confusion
def carbohydrate_requirement_handler(message:Message, user_body_profile:UserBodyProfile):
    isend(username=message.from_user.username, chat_id=message.chat.id, func_name='carbohydrate_requirement_handler', inputted_value=message.text)
    carbohydrate_requirement = message.text
    if carbohydrate_requirement and is_valid_number(carbohydrate_requirement.replace('/', '')):
        carbohydrate_requirement = carbohydrate_requirement.replace('/', '')
        input_diet_macros_context:InputDietMacrosContext = get_input_diet_macros_context(message)
        input_diet_macros_context.carbohydrate = int(carbohydrate_requirement)
        send_nutrient_requirements(message)
    else:
        msg = bot.send_message(message.chat.id, 'Введите значение или нажмите на команду для применения рассчитанного значения')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(msg, carbohydrate_requirement_handler, user_body_profile)

def send_nutrient_requirements(message:Message):
    isend(username=message.from_user.username, chat_id=message.chat.id, func_name='carbohydrate_requirement_handler')
    input_diet_macros_context:InputDietMacrosContext = get_input_diet_macros_context(message)
    average_cals = input_diet_macros_context.protein*NUTRIENT_CALORIES['protein'] + input_diet_macros_context.fat*NUTRIENT_CALORIES['fat'] + input_diet_macros_context.carbohydrate*NUTRIENT_CALORIES['carbohydrate']
    min_cals = int(average_cals-average_cals*0.1)
    max_cals = int(average_cals+average_cals*0.1)
    input_diet_macros_context.calories_range = f'{min_cals}-{max_cals}'
    bot.send_message(message.chat.id,
f'''
Норма КБЖУ
Белки: {input_diet_macros_context.protein}
Жиры: {input_diet_macros_context.fat}
Углеводы: {input_diet_macros_context.carbohydrate}
Калорий: от {min_cals} до {max_cals}
Ваша задача лишь придерживаться обозначенного диапазона калорийности и нутриентов около обозначенных значений в своем дневном рационе.
''',
reply_markup=keyboards.diet_macros_keyboard())
    
def save_user_diet_macros(message:Message):
    isend(username=message.from_user.username, chat_id=message.chat.id, func_name='save_user_diet_macros')
    user_id = db.get_user_id(message.chat.id)
    input_diet_macros_context:InputDietMacrosContext = get_input_diet_macros_context(message)
    db.update_user_diet_macros(user_id=user_id,
                            protein_g=input_diet_macros_context.protein,
                            fat_g=input_diet_macros_context.fat,
                            carbohydrate_g=input_diet_macros_context.carbohydrate,
                            calories_range=input_diet_macros_context.calories_range)
    bot.send_message(message.chat.id,'Изменения сохранены')
    nutritions.process_nutrition(message)