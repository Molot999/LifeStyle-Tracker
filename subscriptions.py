from config import bot
import dbconnection as db
import keyboards
from datetime import timedelta, datetime
from contexts import get_user_context
import yoomoney_api
import random
from user_body_profiles import send_user_body_profile_filling_request
from subscriptions_utils import AvailableSubscription

def check_subscription_status(message):
    if user_subscription_info := db.get_user_subscription_info(message.chat.id):
        _, end_date = user_subscription_info
        # Получаем текущее время
        current_time = datetime.now()
        # Проверяем, что текущее время меньше целевого времени
        if current_time < end_date:
            # Вычисляем разницу между двумя датами
            delta:timedelta = end_date - current_time
            send_subscription_info(message, delta.days)
        else:
            offer_subscription(message)
    else:
        offer_subscription(message)

def offer_subscription(message):
    name = db.get_name(message.chat.id)
    available_subscriptions = [AvailableSubscription(*available_subscription) for available_subscription in db.get_available_subscriptions()]
    bot.send_message(message.chat.id,
                    f'<b>{name}</b>, хочешь купить подписку, чтобы получить доступ ко всему функционалу?',
                    reply_markup=keyboards.offer_subscription(available_subscriptions),
                    parse_mode='HTML')

def send_subscription_info(message, days_left):
    bot.send_message(message.chat.id, f'Оставшееся время подписки: <b>{days_left}</b> д.', parse_mode='HTML')

def buy_subscription(message, period, price):
    username = get_user_context(message).username
    label = f"{username}-{random.randint(1111111111, 9999999999)}"
    payment_url = yoomoney_api.generate_payment_url(price, label)
    db.add_payment(label, payment_url, period)
    bot.send_message(message.chat.id,
f"""
Период подписки: <b>{period} дней</b>
Сумма к оплате: <b>{price} рублей</b>

Способы оплаты:
💳 Банковская карта
🟣 Кошелек ЮMoney
""",
parse_mode='HTML',
reply_markup=keyboards.pay_keyboard(payment_url, label))
    
def apply_test_period(message):
    user_test_period_status = db.get_user_test_period_status(message.chat.id)
    print('user_test_period_status', user_test_period_status)
    if user_test_period_status is False:
        db.update_user_test_period_status(message.chat.id, True)
        db.add_user_subscription(message.chat.id, period_days=7) # Проверить что такого нет
        bot.send_message(message.chat.id, 'Вы получили бесплатные 7 дней подписки 👍')
        
    else:
        bot.send_message(message.chat.id, 'К сожалению, вы уже активировали тестовый период раннее')