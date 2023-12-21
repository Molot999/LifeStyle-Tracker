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
from user_foods_utils import UserFood
import user_foods_file_manager
from utils import generate_random_filename
import random
from user_foods_utils import parse_food_nutrients
from contexts import get_input_new_user_foods_context, InputNewUserFoodsContext
from user_foods import process_user_foods
import threading

def process_user_foods_editing(message:Message):
    user_id = db.get_user_id(message.chat.id)
    user_foods = db.get_user_foods(user_id)
    user_foods_count = len(user_foods) if user_foods else 0
    user_foods_editing_text = f'''
Добавлено: {user_foods_count} шт.
Для добавления своих продуктов загрузите excel-шаблон и загрузите его.
- После основных колонок в шаблоне вы можете добавить свои колонки, указав их название и проставив соответствующие им значения в ячейках каждого продукта.
В дополнительных колонках вы можете разместить, к примеру, информацию о количестве витаминов, минералов и т.д. В таком случае в название колонки впишите название соответствующего витамина или минерала.
- Если не знаете количество нутриентов (калории, белки, жиры, углеводы и т.д.) на 100 грамм продукта, то заполните поле "Вес (грамм)" и проставьте для него соответствующее количество нутриентов, далее бот сам все расчитает.
Чтобы обновить данные скачайте таблицу загруженных вами продуктов, внесите правки и загрузите данный файл в разделе "Обновить"'''
    bot.send_message(message.chat.id, user_foods_editing_text, reply_markup=keyboards.user_foods_editing_keyboard())

def process_uploading_new_user_foods_table(message:Message):
    msg = bot.send_message(message.chat.id, 'Отправьте файл с excel-таблицей')
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(msg, new_user_foods_table_handler)

@cancel_on_message_confusion
def new_user_foods_table_handler(message:Message):
    if message.content_type == 'document':
        document = message.document
        # Получаем объект файла из сообщения
        file_info = bot.get_file(document.file_id)

        # Скачиваем файл
        downloaded_file = bot.download_file(file_info.file_path)

        # Разделение имени файла и его расширения
        file_name_parts = document.file_name.split('.')
        file_extension = file_name_parts[-1]
        file_name = f'{document.file_unique_id}_{generate_random_filename()}'
        file_path = f'user_foods_tables/{file_name}.{file_extension}'
        # Сохраняем файл
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        if user_foods := user_foods_file_manager.get_user_foods_from_excel_file(file_path):
            send_new_user_foods_table_info(message, user_foods)
            return
        else:
            msg = bot.send_message(message.chat.id, 'Ошибка. Не удалось получить данные из таблицы. Проверьте, файл на наличие ошибок и актуальность шаблона и загрузите еще раз:')
    else:
        msg = bot.send_message(message.chat.id, 'Ошибка. Отправьте файл с excel-таблицей')

    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(msg, new_user_foods_table_handler)

def send_new_user_foods_table_info(message:Message, user_foods:List[UserFood]):
    input_new_user_foods_context:InputNewUserFoodsContext = get_input_new_user_foods_context(message)
    input_new_user_foods_context.new_user_foods = user_foods
    bot.send_message(message.chat.id, f'Найдено продуктов: {len(user_foods)}')
    send_new_user_foods_example(message)

def send_new_user_foods_example(message:Message):
    input_new_user_foods_context:InputNewUserFoodsContext = get_input_new_user_foods_context(message)
    if user_foods := input_new_user_foods_context.new_user_foods:
        random_user_food:UserFood = user_foods[random.randint(0, len(user_foods))-1]
        full_nutrients = random_user_food.full_nutrients
        nutrients_dict = parse_food_nutrients(full_nutrients)
        random_nutrients_text = ''
        if any(bool(value) for _, value in nutrients_dict.items()):
            filled_nutrients_dict = {key: value for key, value in nutrients_dict.items() if value}
            print(filled_nutrients_dict)
            keys_list = list(filled_nutrients_dict.keys())
            random_keys = random.sample(keys_list, min(6, len(keys_list)))
            random_nutrients_text = '\n<u>Пример пользовательских колонок</u>:'
            for key in random_keys:
                random_nutrients_text += f'\n{key} - {filled_nutrients_dict[key]}'

        new_user_food_example_text = f'''
Пример:
<b>{random_user_food.title}</b>
Штрихкод: {random_user_food.barcode or 'не установлено'}
Категория: {random_user_food.group_name or 'не установлено'}
Калории: {random_user_food.calories}
Белки: {random_user_food.protein}
Жиры: {random_user_food.fat}
Углеводы: {random_user_food.carbohydrate}{random_nutrients_text}

Все верно?'''

        bot.send_message(message.chat.id,
                        new_user_food_example_text,
                        parse_mode='HTML',
                        reply_markup=keyboards.new_user_foods_table_info_keyboard())
        
    else:
        bot.send_message(message.chat.id, 'Возникла ошибка')

def send_new_user_foods_table_template(message:Message):
    with open('foods_template_v1.xlsx', 'rb') as f:
        bot.send_document(message.chat.id, f)

def save_new_user_foods(message:Message):
    input_new_user_foods_context:InputNewUserFoodsContext = get_input_new_user_foods_context(message)
    user_foods:List[UserFood] = input_new_user_foods_context.new_user_foods
    user_id = db.get_user_id(message.chat.id)
    msg = bot.send_message(message.chat.id, 'Начинаем добавление в базу данных...')
    for i, user_food in enumerate(user_foods):
        i += 1
        user_food.user_id = user_id
        db.add_user_food(user_food)
    bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text='Новые продукты добавлены ✅')
    process_user_foods(message)

def process_downloading_user_foods_table(message:Message):
    user_id = db.get_user_id(message.chat.id)
    if user_foods := db.get_user_foods(user_id):
        bot.send_message(message.chat.id, 'Начинаем формировать файл. Как только он будет готов - сразу пришлем')
        msg = bot.send_message(message.chat.id, 'Обработано продуктов:')
        thread = threading.Thread(target= user_foods_file_manager.get_user_foods_table, args=(user_foods, msg))
        thread.start()
    else:
        bot.send_message(message.chat.id, 'Вы еще не заносили свои продукты')

def process_deleting_user_foods(message:Message):
    bot.send_message(message.chat.id, 'Вы уверены, что хотите удалить все внесенные продукты?', reply_markup=keyboards.user_foods_delete_checking_keyboard())

def delete_user_foods(message:Message):
    user_id = db.get_user_id(message.chat.id)
    db.delete_user_foods(user_id)
    bot.send_message(message.chat.id, 'Данные удалены')
    process_user_foods_editing(message)