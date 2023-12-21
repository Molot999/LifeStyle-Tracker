from config import bot
import dbconnection as db
import datetime
import random

# def my_decorator(func):
#     def wrapper(message, *args, **kwargs):
#         result = func(*args, **kwargs)
#         return result
#     return wrapper

def send_need_subscription_message(message):
    bot.send_message(message.chat.id, 'Для доступа к полному функционалу сервиса необходимо приобрести подписку')

def parse_date(date_string):
    date_format = "%d.%m.%Y %H:%M:%S"
    try:
        return datetime.datetime.strptime(date_string, date_format)
    except ValueError as ve:
        print("Некорректный формат даты!", ve)
        return None

def get_minutes_diff(start_date:datetime, end_date:datetime) -> int:
    timedelta = end_date - start_date
    return int(timedelta.total_seconds() / 60)

def format_date(date:datetime):
    return date.strftime("%d.%m.%Y %H:%M") if date else ''

def get_now_date(format=None) -> str:
    if not format:
        return datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    else:
        return datetime.datetime.now().strftime(format)

def calculate_age(birthdate_str):
    """
    Рассчитывает количество лет по дате рождения в формате DD.MM.YYYY.

    Параметры:
    birthdate_str (str): Дата рождения в формате DD.MM.YYYY.

    Возвращает:
    int: Количество лет.
    """
    # Получаем текущую дату
    current_date = datetime.datetime.now()

    # Преобразуем строку с датой рождения в объект datetime
    birthdate = datetime.datetime.strptime(birthdate_str, "%d.%m.%Y")

    # Рассчитываем разницу между текущей датой и датой рождения
    age_timedelta = current_date - birthdate

    # Получаем количество лет из timedelta и возвращаем результат
    return age_timedelta.days // 365

# Функция для генерации случайного имени файла
def generate_random_filename(len=16):
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    return ''.join(random.choice(letters) for _ in range(len))

if __name__ == '__main__':
    print(generate_random_filename(5))