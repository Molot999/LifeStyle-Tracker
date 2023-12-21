from config import bot
import subscriptions
import dbconnection as db
import keyboards
from contexts import get_user_context, get_input_timezone_context, UserContext, InputTimeZoneContext
from informer import isend
from telebot.types import Message, Location, User
from decorators import cancel_on_message_confusion
from user_timezone import get_timezone
import re

def set_name(message:Message):
    isend(username=message.from_user.username, chat_id=message.chat.id, func_name='set_name', inputted_value=message.text)
    if name := message.text:
        if name not in ['/start', '🍽️Питание', '💪Тренировки', '💬Поддержка', '👤Профиль', '🔢Калькуляторы']:
            user_context:UserContext = get_user_context(message)
            db.add_user(user_context.username, message.chat.id, name)
            bot.send_message(message.chat.id, f'Приятно познакомиться, <b>{name}</b>', parse_mode='HTML')
            process_location(message)
            #subscriptions.check_subscription_status(message)
        else:
            send_error_message(message)
    else:
        send_error_message(message)

def print_user_timezone(message:Message):
    user_id = db.get_user_id(message.chat.id)
    if user_timezone := db.get_user_timezone(user_id):
        edit = True
        user_timezone_text = f'Ваш часовой пояс: {user_timezone}'
    else:
        edit = False
        user_timezone_text = 'Часовой пояс не установлен'
    bot.send_message(message.chat.id, user_timezone_text, reply_markup=keyboards.user_timezone_keyboard(edit))

def send_processing_timezone_message(message:Message):
    user_id = db.get_user_id(message.chat.id)
    msg = bot.send_message(message.chat.id, 'Отправь свою геопозицию или укажи часовой пояс в формате UTC (например: +07:00), так я смогу выводить записи из дневников в соответствии с местным временем:')
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(msg, location_handler, user_id)

def process_location(message:Message):
    user_id = db.get_user_id(message.chat.id)
    if not db.get_user_timezone(user_id):
        send_processing_timezone_message(message)
    else:
        bot.send_message('Окей, продолжим', reply_markup=keyboards.main_keyboard())

@cancel_on_message_confusion
def location_handler(message:Message, user_id):
    input_timezone_context:InputTimeZoneContext = get_input_timezone_context(message)
    if message.content_type == 'location':
        location:Location = message.location
        latitude = location.latitude
        longitude = location.longitude
        timezone = get_timezone(latitude, longitude)
        input_timezone_context.timezone = timezone
        send_inputted_timezone(message, timezone)
        return
    elif message.content_type == 'text':
        timezone = message.text
        pattern = r'^[+-]\d{2}:\d{2}$'
        if re.match(pattern, timezone) is not None:
            input_timezone_context.timezone = timezone
            save_timezone(message)
            return
        else:
            msg = bot.send_message(message.chat.id, 'Ошибка. Неверный формат часового пояса. Попробуйте еще раз:')
    else:
        msg = bot.send_message(message.chat.id, 'Ошибка. Отправьте локацию или напишите часовой пояс:')

    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(msg, location_handler, user_id)

def send_inputted_timezone(message:Message, timezone):
    bot.send_message(message.chat.id, f'Ваш часовой пояс (UTC): {timezone}. Верно?', reply_markup=keyboards.check_timezone_keyboard())

def send_timezone_set(message:Message):
    bot.send_message(message.chat.id, 'Часовой пояс установлен ✅', reply_markup=keyboards.main_keyboard())

def save_timezone(message:Message):
    user_id = db.get_user_id(message.chat.id)
    input_timezone_context:InputTimeZoneContext = get_input_timezone_context(message)
    if timezone := input_timezone_context.timezone:
        db.set_user_timezone(user_id, timezone)
        send_timezone_set(message)
    else:
        msg = bot.send_message(message.chat.id, 'Произошла ошибка. Заново введите часовой пояс или пришлите геолокацию:')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(msg, location_handler, user_id)

def send_error_message(message:Message):
    msg = bot.send_message(message.chat.id, 'Ошибка. Введите свое имя:')
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(msg, set_name)