import dbconnection as db
import datetime
from config import bot
from telebot.types import Message

class UserSubscriptionStatus:
    def __init__(self, chat_id) -> None:
        self._chat_id = chat_id
        self._timestamp = None
        self._status = None

    @property
    def status(self):
        if self._status and self._timestamp:
            diff = datetime.datetime.now() - self._timestamp
            if diff.total_seconds() > 3 * 3600:
                self.__update_status()
        else:
            self.__update_status()
        return self._status
    
    def __update_status(self):
        if user_subscription_info := db.get_user_subscription_info(self._chat_id):
            _, end_date = user_subscription_info
            current_time = datetime.datetime.now()
            self._status = current_time < end_date
            self._timestamp = current_time
        else:
            self._status = False
            self._timestamp = datetime.datetime.now()

user_subscriptions_statuses = {}

def check_subscription(func):
    def wrapper(message:Message):
        if subscription_status := has_active_subscription(message.chat.id):
            print('Статус подписки:', subscription_status)
            func(message)
        else:
            bot.send_message(message.chat.id, "Для продолжения требуется подписка")
    return wrapper

def has_active_subscription(chat_id):
    if chat_id not in user_subscriptions_statuses:
        user_subscriptions_statuses[chat_id] = UserSubscriptionStatus(chat_id)
    user_subscriptions_status:UserSubscriptionStatus = user_subscriptions_statuses[chat_id]
    return user_subscriptions_status.status

def update_user_subscription_status(chat_id):
    pass