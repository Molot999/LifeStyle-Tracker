from config import bot
from telebot.types import Message

def send_user_foods_file(message:Message, filepath):
    if filepath:
        with open(filepath, 'rb') as f:
            bot.send_document(message.chat.id, f)
    else:
        bot.send_message(message.chat.id, 'Не удалось отправить файл. Попробуйте еще раз или обратитесь в поддержку')

def edit_download_processed_count_message_text(message:Message, count=0, value=0, is_finished=False):
    if is_finished:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Файл готов ✅')
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f'Обработано продуктов: {value} из {count}')

# def edit_upload_processed_count_message_text(message:Message, count, value):
#     bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f'Добавлено продуктов: {value} из {count}')