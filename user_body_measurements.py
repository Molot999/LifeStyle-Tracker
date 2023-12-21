from config import bot
from telebot.types import Message
import dbconnection as db
from contexts import get_user_context, get_input_body_measurements_context, UserContext, InputBodyMeasurements
from user_body_measurements_utils import BodyMeasurements
import keyboards
from typing import List
from user_body_profile_utils import is_valid_number
from utils import get_now_date
from decorators import cancel_on_message_confusion
from informer import isend
from user_body_profiles import print_user_body_profile_info
import datetime
from subscriptions_manager import check_subscription

MEASUREMENTS_TEXT = {
    'shoulders': 'Плечи',
    'forearms': 'Предплечья',
    'biceps': 'Бицепсы',
    'chest': 'Грудная клетка',
    'waist': 'Талия',
    'thighs': 'Бедра',
    'calves': 'Голень',
    'neck': 'Шея'
}

def print_user_body_measurements_diary(message:Message):
    user_id = db.get_user_id(message.chat.id)
    if user_body_measurements := db.get_user_body_measurements(user_id):
        text = 'Чтобы просмотреть информацию по замерам нажмите на команду слева:'
        for num, measurement in enumerate(user_body_measurements, 1):
            measurement.number = num
            # Преобразуем строку в объект datetime
            date_time_obj = datetime.datetime.strptime(measurement.datetime, "%d.%m.%Y %H:%M:%S")
            # Форматируем объект datetime обратно в строку без секунд
            formatted_date_time_str = date_time_obj.strftime("%d.%m.%Y %H:%M")
            text += f'\n/{num} {formatted_date_time_str}'
        has_entries = True
    else:
        text = 'Вы еще не вносили замеры'
        has_entries = False

    msg = bot.send_message(message.chat.id, text, reply_markup=keyboards.user_meausurements_keyboard())
    if has_entries:
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(msg, user_body_measurement_num_handler, user_body_measurements)
    # else:
    #     print_user_body_profile_info(message)

@cancel_on_message_confusion
def user_body_measurement_num_handler(message:Message, user_body_measurements:List[BodyMeasurements]):
    if body_measurement_num_command := message.text:
        body_measurement_num_str = body_measurement_num_command.replace('/', '')
        if body_measurement_num_str.isdigit() and int(body_measurement_num_str) in [user_body_measurement.number for user_body_measurement in user_body_measurements]:
            body_measurement_num = int(body_measurement_num_str)
            if selected_body_measurement_list := [
                user_body_measurement
                for user_body_measurement in user_body_measurements
                if user_body_measurement.number == body_measurement_num
            ]:
                selected_body_measurement:BodyMeasurements = selected_body_measurement_list[0]
                body_measurement_info_text = f'''
Плечи: {selected_body_measurement.shoulders or 'не заполнено'}
Предплечья: {selected_body_measurement.forearms or 'не заполнено'}
Бицепсы: {selected_body_measurement.biceps or 'не заполнено'}
Грудная клетка: {selected_body_measurement.chest or 'не заполнено'}
Талия: {selected_body_measurement.waist or 'не заполнено'}
Бедра: {selected_body_measurement.thighs or 'не заполнено'}
Голень: {selected_body_measurement.calves or 'не заполнено'}
Шея: {selected_body_measurement.neck or 'не заполнено'}'''
                msg = bot.send_message(message.chat.id, body_measurement_info_text, reply_markup=keyboards.delete_body_measurements_entry_keyboard(selected_body_measurement.id))
                if len(user_body_measurements) > 1:
                    print_user_body_measurements_diary(message)
                return
            else:
                msg = bot.send_message(message.chat.id, 'Возникла ошибка. Попробуйте еще раз')
        else:
            msg = bot.send_message(message.chat.id, 'Ошибка. Неверная команда')
    else:
        msg = bot.send_message(message.chat.id, 'Ошибка. Нажмите на соответствующую команду')

    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(msg, user_body_measurement_num_handler, user_body_measurements)

@check_subscription
def process_body_measurements_adding(message:Message):
    input_body_measurements_context:InputBodyMeasurements = get_input_body_measurements_context(message)
    input_body_measurements_context.clear()
    process_body_measurements_field_adding(message)

def process_body_measurements_field_adding(message:Message):
    input_body_measurements_context:InputBodyMeasurements = get_input_body_measurements_context(message)
    measurements = input_body_measurements_context.measurements
    if uniputted_keys := [
        measurement_key
        for measurement_key, value in measurements.items()
        if value is None
    ]:
        first_uniputted_key = uniputted_keys.pop()
        msg = bot.send_message(message.chat.id, f'Введите значение для <b>{MEASUREMENTS_TEXT.get(first_uniputted_key)}</b>', parse_mode='HTML')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(msg, body_measurement_value_handler, first_uniputted_key)
    else:
        user_id = db.get_user_id(message.chat.id)
        db.add_user_body_measurements(user_id=user_id,
                                    shoulders=measurements.get('shoulders'),
                                    forearms=measurements.get('forearms'),
                                    biceps=measurements.get('biceps'),
                                    chest=measurements.get('chest'),
                                    waist=measurements.get('waist'),
                                    thighs=measurements.get('thighs'),
                                    calves=measurements.get('calves'),
                                    neck=measurements.get('neck'),
                                    datetime_str=get_now_date())
        bot.send_message(message.chat.id, 'Замеры сохранены')
        print_user_body_measurements_diary(message)

@cancel_on_message_confusion
def body_measurement_value_handler(message:Message, uniputted_key):
    if body_measurement_value_str := message.text:
        if is_valid_number(body_measurement_value_str):
            input_body_measurements_context:InputBodyMeasurements = get_input_body_measurements_context(message)
            measurements = input_body_measurements_context.measurements
            measurements[uniputted_key] = float(body_measurement_value_str)
            process_body_measurements_field_adding(message)
        else:
            msg = bot.send_message(message.chat.id, 'Ошибка. Введено некорректное значение. Попробуйте еще раз:')
            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(msg, body_measurement_value_handler, uniputted_key)
    else:
        msg = bot.send_message(message.chat.id, 'Ошибка. Введите значение:')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(msg, body_measurement_value_handler, uniputted_key)

def delete_body_measurements_entry(message:Message, body_measurements_id):
    if body_measurements_id:
        try:
            db.delete_user_body_measurements_entry(body_measurements_id)
            bot.send_message(message.chat.id, 'Запись удалена')
        except Exception as e:
            print('Ошибка! delete_body_measurements_entry():', e)
            bot.send_message(message.chat.id, 'Произошла ошибка при удалении записи')
    else:
        bot.send_message(message.chat.id, 'Произошла ошибка. Запись не найдена')
    print_user_body_measurements_diary(message)