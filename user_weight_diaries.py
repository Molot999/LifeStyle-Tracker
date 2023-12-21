from config import bot
from telebot.types import Message
import dbconnection as db
from user_weight_diaries_utils import UserWeightDiaryEntry
from typing import List
from contexts import get_user_context, UserContext
import keyboards
from utils import get_now_date
from user_body_profile_utils import is_valid_number
from decorators import cancel_on_message_confusion
from user_body_profiles import print_user_body_profile_info, update_user_body_profile
import datetime
from user_body_profile_classes import UserBodyProfile
from subscriptions_manager import check_subscription

def print_user_weight_diary(message:Message):
    user_id = db.get_user_id(message.chat.id)
    if weight_diary_entries := db.get_user_weight_diary(user_id):
        weight_diary_entries_text = ""
        for num, weight_diary_entry in enumerate(weight_diary_entries, 1):
            weight_diary_entry.number = num
            # Преобразуем строку в объект datetime
            date_time_obj = datetime.datetime.strptime(weight_diary_entry.datetime, "%d.%m.%Y %H:%M:%S")
            # Форматируем объект datetime обратно в строку без секунд
            formatted_date_time_str = date_time_obj.strftime("%d.%m.%Y %H:%M")
            entry_text = f'/{num} {weight_diary_entry.weight} - {formatted_date_time_str}'
            weight_diary_entries_text += entry_text + '\n'
        weight_diary_entries_text += f'\nЧтобы просмотреть подробную информацию о записи нажмите на соответствующую команду слева'
        has_entries = True
    else:
        weight_diary_entries_text = 'Замеров веса пока что не было'
        has_entries = False

    msg = bot.send_message(message.chat.id, weight_diary_entries_text, reply_markup=keyboards.user_weight_diary_keyboard())
    if has_entries:
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(msg, user_weight_diary_entry_num_handler, weight_diary_entries)
    # else:
    #     print_user_body_profile_info(message)

@cancel_on_message_confusion
def user_weight_diary_entry_num_handler(message:Message, weight_diary_entries:List[UserWeightDiaryEntry]):
    if message.text:
        user_weight_diary_entry_num = str(message.text).replace('/', '')
        if user_weight_diary_entry_num.isdigit() and int(user_weight_diary_entry_num) in [weight_diary_entry.number for weight_diary_entry in weight_diary_entries]:
            user_weight_diary_entry_list = [weight_diary_entry for weight_diary_entry in weight_diary_entries if weight_diary_entry.number == int(user_weight_diary_entry_num)]
            if len(user_weight_diary_entry_list) > 0:
                user_weight_diary_entry:UserWeightDiaryEntry = user_weight_diary_entry_list[0]
            else:
                bot.send_message(message.chat.id, 'Произошла ошибка при получении записи из дневника питания')
                print_user_weight_diary(message)
                return
            # Преобразуем строку в объект datetime
            date_time_obj = datetime.datetime.strptime(user_weight_diary_entry.datetime, "%d.%m.%Y %H:%M:%S")
            # Форматируем объект datetime обратно в строку без секунд
            formatted_date_time_str = date_time_obj.strftime("%d.%m.%Y %H:%M")
            user_weight_diary_entry_text = f'''
<b>Вес</b>: {user_weight_diary_entry.weight}
<b>Время внесения</b>: {formatted_date_time_str}'''
            bot.send_message(message.chat.id, user_weight_diary_entry_text, parse_mode='HTML', reply_markup=keyboards.delete_weight_diary_entry_keyboard(user_weight_diary_entry.id))
            if len(weight_diary_entries) > 1:
                print_user_weight_diary(message)
            return
        else:
            msg = bot.send_message(message.chat.id, 'Ошибка. Отправлена некорректная команда. Попробуйте еще раз:')
    else:
        msg = bot.send_message(message.chat.id, 'Выберите ID записи в дневнике веса:')
    
    bot.clear_step_handler_by_chat_id(message.chat.id)    
    bot.register_next_step_handler(msg, user_weight_diary_entry_num_handler, weight_diary_entries)

@check_subscription
def process_user_weight_diary_entry_adding(message:Message):
    bot.send_message(message.chat.id, 'Введите свой вес в килограммах (например: 80.3) или нажмите /cancel для отмены:')
    bot.register_next_step_handler(message, user_weight_diary_entry_handler)

@cancel_on_message_confusion
def user_weight_diary_entry_handler(message:Message):
    if message.text == '/cancel':
        print_user_weight_diary(message)
    elif message.text and is_valid_number(message.text):
        user_id = db.get_user_id(message.chat.id)
        new_weight = message.text
        db.add_user_weight_diary_entry(user_id, new_weight, get_now_date())
        bot.send_message(message.chat.id, 'Запись успешно добавлена')
        update_user_body_profile(message, new_weight)
        print_user_weight_diary(message)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Введите свой вес или нажмите /cancel для отмены:')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(message, user_weight_diary_entry_handler)

def delete_weight_diary_entry(message:Message, weight_diary_entry_id):
    if weight_diary_entry_id:
        try:
            db.delete_user_weight_diary_entry(weight_diary_entry_id)
            user_id = db.get_user_id(message.chat.id)
            weight_diary_entries = db.get_user_weight_diary(user_id)
            if weight_diary_entries and len(weight_diary_entries) > 0:
                last_weight = weight_diary_entries[0].weight
            else:
                user_body_profile:UserBodyProfile = db.get_user_body_profile(user_id)
                last_weight = user_body_profile.weight
            update_user_body_profile(message, last_weight)
            bot.send_message(message.chat.id, 'Запись удалена')
        except Exception as e:
            print('Ошибка! delete_weight_diary_entry():', e)
            bot.send_message(message.chat.id, 'Произошла ошибка при удалении записи')
    else:
        bot.send_message(message.chat.id, 'Произошла ошибка. Запись не найдена')
    print_user_weight_diary(message)