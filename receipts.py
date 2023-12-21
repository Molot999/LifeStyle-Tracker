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

def process_receipts(message:Message):
    isend(chat_id=message.chat.id, username=message.from_user.username, func_name='process_receipts')
    bot.send_message(message.chat.id, 'Здесь вы сможете подыскать интересный рецепт. База формируется из рецептов, которые присутствуют в интернете', reply_markup=keyboards.receipts_keyboard())

def process_random_receipt(message:Message):
    isend(chat_id=message.chat.id, username=message.from_user.username, func_name='process_random_receipt')
    if receipt := db.get_random_receipt():
        receipt_info_text = get_receipt_info_text(receipt)
        bot.send_message(message.chat.id, receipt_info_text, parse_mode='HTML', reply_markup=keyboards.random_receipt_keyboard())
    else:
        bot.send_message(message.chat.id, 'Извините, произошла ошибка :(')

def process_receipt_searching(message:Message):
    isend(chat_id=message.chat.id, username=message.from_user.username, func_name='process_receipt_searching')
    bot.send_message(message.chat.id, 'Введите название рецепта, а мы предложим подходящие варианты:')
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(message, receipt_title_handler)

@cancel_on_message_confusion
def receipt_title_handler(message:Message):
    isend(chat_id=message.chat.id, username=message.from_user.username, func_name='receipt_title_handler', inputted_value=message.text)
    if receipt_title := message.text:
        if found_receipts := receipt_searcher.process_receipt_searching(receipt_title):
            send_found_receipts(message, found_receipts)
            return
        else:
            bot.send_message(message.chat.id, 'Подходящих рецептов не нашлось. Попробуйте еще раз:')
    else:
        bot.send_message(message.chat.id, 'Введите название рецепта:')

    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(message, receipt_title_handler)

def send_found_receipts(message:Message, found_receipts:List[Receipt]):
    isend(chat_id=message.chat.id, username=message.from_user.username, func_name='send_found_receipts')
    receipts_list_text = 'Нажмите на команду слева, чтобы просмотреть рецепт:'
    for receipt in found_receipts:
        receipts_list_text += f'\n/{receipt.id} <b>{receipt.title}</b>'
    bot.send_message(message.chat.id, receipts_list_text, parse_mode='HTML')
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(message, receipt_id_handler, found_receipts)

@cancel_on_message_confusion
def receipt_id_handler(message:Message, found_receipts):
    isend(chat_id=message.chat.id, username=message.from_user.username, func_name='receipt_id_handler', inputted_value=message.text)
    if message.text:
        receipt_id = str(message.text).replace('/', '')
        if is_valid_number(receipt_id):
            if receipt := [receipt for receipt in found_receipts if str(receipt.id) == receipt_id][0]:
                receipt_info_text = get_receipt_info_text(receipt)
                bot.send_message(message.chat.id, receipt_info_text, parse_mode='HTML')
                return
            else:
                bot.send_message(message.chat.id, 'Рецепт не найден. Попробуйте еще раз:')
        else:
            bot.send_message(message.chat.id, 'Некорректная команда. Попробуйте еще раз:')
    else:
        bot.send_message(message.chat.id, 'Нажмите на команду слева, чтобы просмотреть рецепт:')

    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(message, receipt_id_handler)

def get_receipt_info_text(receipt:Receipt):
    isend(func_name='get_receipt_info_text')
    receipt_ingredients:List[ReceiptIngredient] = db.get_receipt_ingredients(receipt.id)
    receipt_info_text = f'''
<b>{receipt.title}</b> ({receipt.id})
{receipt.category_1} -> {receipt.category_2} -> {receipt.category_3}
Описание: {receipt.description}
<u>Пищевая ценность (100 г)</u>:
Калории: {receipt.calories_100g}
Белки: {receipt.proteins_100g}
Жиры: {receipt.fats_100g}
Углеводы: {receipt.carbohydrates_100g}'''
    if receipt_ingredients:
        receipt_info_text += '\n<u>Ингредиенты</u>:'
        for receipt_ingredient in receipt_ingredients:
            title = receipt_ingredient.title
            weight = f' - {receipt_ingredient.weight}' if receipt_ingredient.weight else ''
            receipt_info_text += f'\n{title}{weight}'
    receipt_info_text += f'\n\nИсточник: {receipt.url}'
    return receipt_info_text