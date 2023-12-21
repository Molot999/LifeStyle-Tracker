from telebot.types import Message
from config import bot
import dbconnection as db
from contexts import get_user_context, UserContext
from user_body_profile_classes import UserBodyProfile
import utils
import calculator_formulas
from decorators import cancel_on_message_confusion
import re
from informer import isend

calculators = {'maxhr':('Максимальная частота сердечных сокращений (ЧСС)',
                        'Формула для расчета максимальной частоты сердечных сокращений (ЧСС) - это способ приближенно определить самое высокое количество сердечных ударов в минуту, которое ваше сердце может достигнуть во время максимального физического усилия. Эта формула основана на средних данных и может использоваться для первоначального предположения значения максимальной ЧСС.'),
                'onerm':('Одноповторый максимум', 'Формулы для расчета максимального веса в упражнении, который вы сможете поднять 1 раз')
}

def send_calculators_message(message:Message, again=False):
    isend(username=message.from_user.username, chat_id=message.chat.id, func_name='send_calculators_message')
    msg = '' if again else 'Нажмите на соответствующую команду слева, чтобы начать расчет:'
    for command, data in calculators.items():
        name = data[0]
        msg += f'\n/{command} - {name}'
    bot.send_message(message.chat.id, msg)
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(message, calculator_command_handler)

@cancel_on_message_confusion
def calculator_command_handler(message:Message):
    isend(username=message.from_user.username, chat_id=message.chat.id, func_name='calculator_command_handler', inputted_value=message.text)
    calculator_command = str(message.text).replace('/', '')
    if calculator_command == 'maxhr':
            bot.send_message(message.chat.id, 'Введите возраст:')
            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(message, age_handler, 'maxhr')
    elif calculator_command == 'onerm':
        bot.send_message(message.chat.id, 'Введите вес и количество повторений с ним (например: 60x12 или 75.5x5):')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(message, weight_reps_handler, 'onerm')
    else:
        bot.send_message(message.chat.id, 'Команда не найдена. Попробуйте еще раз:')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(message, calculator_command_handler)

@cancel_on_message_confusion
def age_handler(message:Message, formula:str):
    isend(text=f'Формула - {formula}', username=message.from_user.username, chat_id=message.chat.id, func_name='age_handler', inputted_value=message.text)
    age = str(message.text)
    if age.isdigit():
        if formula == 'maxhr':
            maxhr_str = calculator_formulas.maxhr(age)
            bot.send_message(message.chat.id, f'Максимальная ЧСС для вас - <b>{maxhr_str}</b>', parse_mode='HTML')
            send_calculators_message(message, True)
    else:
        bot.send_message(message.chat.id, 'Введите возраст (например: 23):')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(message, age_handler, formula)

@cancel_on_message_confusion
def weight_reps_handler(message:Message, formula:str):
    isend(text=f'Формула - {formula}', username=message.from_user.username, chat_id=message.chat.id, func_name='age_handler', inputted_value=message.text)
    if weight_reps_msg := message.text:
        if re.match(r'^\d+(\.\d+)?x\d+(\.\d+)?$', weight_reps_msg) is not None:
            weight, reps = weight_reps_msg.split('x')
            weight = float(weight)
            reps = int(reps)
            if formula == 'onerm':
                onerm_message_text = f'''
Формула №1: {calculator_formulas.onerm_langer_formula(weight, reps)}
Формула №2: {calculator_formulas.onerm_mayhew_watanabe_formula(weight, reps)}
Формула №3: {calculator_formulas.onerm_repsch_formula(weight, reps)}
'''
                bot.send_message(message.chat.id, onerm_message_text)
                send_calculators_message(message, True)
        else:
            bot.send_message(message.chat.id, 'Ошибка. Введите вес и количество повторений в формате ВесxПовторения (например: 100x2):')
            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(message, weight_reps_handler, formula)
    else:
        bot.send_message(message.chat.id, 'Введите вес и количество повторений:')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(message, weight_reps_handler, formula)