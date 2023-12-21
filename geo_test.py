from config import bot
from telebot import types

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    location_button = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    markup.add(location_button)

    bot.send_message(message.chat.id, "Привет! Нажми на кнопку ниже, чтобы отправить свое местоположение.", reply_markup=markup)

# Обработчик местоположения
@bot.message_handler(content_types=['location'])
def handle_location(message):
    latitude = message.location.latitude
    longitude = message.location.longitude

    bot.send_message(message.chat.id, f"Получено местоположение: Широта {latitude}, Долгота {longitude}")

# Запуск бота
if __name__ == '__main__':
    bot.polling(non_stop=True)