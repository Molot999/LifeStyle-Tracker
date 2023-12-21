from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime, timedelta
import re

def get_timezone(lat, lon):
    tz_finder = TimezoneFinder()
    if timezone_str := tz_finder.timezone_at(lng=lon, lat=lat):
        # Получаем объект часового пояса
        tz = pytz.timezone(timezone_str)
        # Получаем разницу времени с UTC+0
        utcoffset = tz.utcoffset(datetime.utcnow())
        
        # Вычисляем знак времени смещения
        sign = '-' if utcoffset.total_seconds() < 0 else '+'
        
        # Получаем абсолютное значение смещения и разбиваем на часы и минуты
        utcoffset = abs(utcoffset)
        hours, seconds = divmod(utcoffset.seconds, 3600)
        minutes = seconds // 60
        
        # Форматируем вывод с учетом знака и добавляем нули в начало
        return f"{sign}{hours:02}:{minutes:02}"
    else:
        return None

def convert_to_user_local_time(entry_time_str, user_timezone_diff, datetime_pattern='%Y.%m.%d %H:%M'):
    match = re.match(r'([-+])(\d{2}):(\d{2})', user_timezone_diff)
    sign = match[1]
    hours = int(match[2])
    minutes = int(match[3])

    # Парсинг времени записи
    entry_time = datetime.strptime(entry_time_str, datetime_pattern)
    time_diff = timedelta(hours=hours, minutes=minutes)
    
    # Преобразование времени записи в местное время пользователя
    user_local_time = entry_time.replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.UTC) + time_diff if sign == '+' else entry_time.replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.UTC) - time_diff
    
    return datetime.strftime(user_local_time, '%Y.%m.%d %H:%M')

def convert_to_db_time(user_local_time_str, user_timezone_diff, datetime_pattern='%Y.%m.%d %H:%M'):
    match = re.match(r'([-+])(\d{2}):(\d{2})', user_timezone_diff)
    sign = match[1]
    hours = int(match[2])
    minutes = int(match[3])
    moscow_timezone_hours = 0
    time_difference_hours = hours - moscow_timezone_hours if sign == '+' else hours + moscow_timezone_hours
    # Преобразование разницы в минуты
    time_difference_minutes = time_difference_hours * 60 + minutes if sign == '+' else time_difference_hours * 60 - minutes
    # Разбиваем разницу в минутах на часы и минуты
    hours, minutes = divmod(time_difference_minutes, 60)
    # Парсинг строки в объект datetime
    date_time_obj = datetime.strptime(user_local_time_str, datetime_pattern)
    # Создание интервала времени для добавления
    time_to_add = timedelta(hours=hours, minutes=minutes)
    new_date_time_obj = date_time_obj - time_to_add if sign == '+' else date_time_obj + time_to_add
    return new_date_time_obj.strftime(datetime_pattern)

if __name__ == '__main__':
    user_local_time = "2023.08.13 03:12"
    user_timezone_diff = "+07:00"

    db_time = convert_to_db_time(user_local_time, user_timezone_diff)
    print(db_time)  # Результат будет временем, скорректированным для БД

    #print(convert_to_db_time('2023.08.12 23:19', '+7:00'))
    # Пример использования функции
    # entry_time_str = "2023.08.13 03:06"  # Пример времени записи
    # user_timezone_diff = "+07:00"       # Пример разницы времени пользователя

    # user_local_time = convert_to_user_local_time(entry_time_str, user_timezone_diff)
    # print("Время записи в местном времени пользователя:", user_local_time)

# latitude = 54.996391  # Пример координат широты
# longitude = 82.897493  # Пример координат долготы

# timezone = get_timezone(latitude, longitude)

# print(timezone)
