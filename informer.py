from config import bot, INFORMER_CHAT_ID, ON_INFORMER
import threading
import time

# Очередь для отложенных сообщений
message_queue = []
queue_lock = threading.Lock()

def isend(text=None, username=None, chat_id=None, func_name=None, inputted_value=None):
    if ON_INFORMER:
        informer_text = f'<b>USERNAME</b>: {username}, <b>CHAT_ID</b>: {chat_id}'
        if func_name:
            informer_text += f'\n<b>Функция</b>: {func_name}'
        if inputted_value:
            informer_text += f'\n<b>Введено</b>: {inputted_value}'
        informer_text += f'\n>{text}'

        #bot.send_message(INFORMER_CHAT_ID, informer_text, parse_mode='HTML')
        add_to_queue(informer_text)

# Функция для добавления сообщения в очередь
def add_to_queue(informer_text):
    with queue_lock:
        message_queue.append(informer_text)

# Функция для отправки сообщений из очереди с задержкой
def send_messages_from_queue():
    while True:
        with queue_lock:
            if message_queue:
                informer_text = message_queue.pop(0)
                bot.send_message(INFORMER_CHAT_ID, informer_text, parse_mode='HTML')
        time.sleep(3)

# Запускаем поток для отправки сообщений из очереди
sender_thread = threading.Thread(target=send_messages_from_queue)
sender_thread.daemon = True
sender_thread.start()