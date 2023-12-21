import dbconnection as db
from config import bot
from telebot.types import Message
import time
from config import IS_TEST

def send_notifications(text, disable_notification=False):
    if IS_TEST:
        return
    user_chat_ids = db.get_user_chat_ids()
    send_notifications_count = 0
    for i, chat_id in enumerate(user_chat_ids):
        try:
            bot.send_message(chat_id, text, disable_notification=disable_notification)
            send_notifications_count += 1
        except Exception as e:
            print('Ошибка в send_notifications()', e)
        finally:
            time.sleep(5)
            print(f'Обработано уведомлений {i+1}/{len(user_chat_ids)}')
    print(f'Отправка уведомлений окончена! Отправлено {send_notifications_count} из {len(user_chat_ids)}')