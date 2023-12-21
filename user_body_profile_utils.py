import re

def is_valid_birth_date(date_string) -> bool:
    # Регулярное выражение для проверки формата DD.MM.YYYY
    date_pattern = r'^\d{2}\.\d{2}\.\d{4}$'
    # Проверяем соответствие регулярному выражению
    if re.match(date_pattern, date_string):
        return True
    else:
        return False

def is_valid_number(number_string):
    # Регулярное выражение для проверки целых чисел и чисел с плавающей точкой
    number_pattern = r'^[-+]?\d+(\.\d+)?$'
    # Проверяем соответствие регулярному выражению
    if re.match(number_pattern, number_string):
        valid_number = True
    else:
        valid_number = False
    return valid_number and is_non_negative_number(number_string)

def is_non_negative_number(number_string):
    try:
        number = float(number_string)
        if number >= 0:
            return True
        else:
            return False
    except ValueError:
        return False

if __name__ == '__main__':
    print(is_valid_number('424.2'))