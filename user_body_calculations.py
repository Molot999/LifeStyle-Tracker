def calculate_bmi(weight_kg, height_m):
    """
    Рассчитывает индекс массы тела (BMI) по заданному весу и росту.
    
    Параметры:
    weight_kg (float): Вес в килограммах.
    height_m (float): Рост в метрах.
    
    Возвращает:
    float: Значение индекса массы тела (BMI).
    """
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)

def calculate_bmr_mifflin(weight_kg, height_cm, age, sex):
    """
    Рассчитывает базовый обмен веществ (BMR) по формуле Миффлина-Сан Жеора.

    Параметры:
    weight_kg (float): Вес в килограммах.
    height_cm (float): Рост в сантиметрах.
    age (int): Возраст в годах.
    sex (str): Пол

    Возвращает:
    float: Значение базового обмена веществ (BMR).
    """
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age
    bmr = bmr + 5 if sex == 'male' else bmr - 161
    return int(round(bmr, 0))

def calculate_tdee(bmr, activity_level_coefficient):
    """
    Рассчитывает общую энергию, расходуемую в день (TDEE) с учетом уровня активности.

    Параметры:
    bmr (float): Значение базового обмена веществ (BMR).
    activity_level (float): Уровень активности.

    Возвращает:
    float: Значение общей энергии, расходуемой в день (TDEE).
    """
    return int(round(bmr * activity_level_coefficient, 0))

def calculate_calorie_range(tdee, goal):
    """
    Рассчитывает диапазон калорий для похудения или наращивания мышц.

    Параметры:
    tdee (float): Общая энергия, расходуемая в день (TDEE).
    goal (str): Цель - 'LOSS_WEIGHT' или 'BUILD_MUSCLE'.

    Возвращает:
    tuple: Кортеж с двумя значениями - минимальное и максимальное количество калорий.
    """
    if goal == 'LOSS_WEIGHT':
        # Чтобы похудеть, создаем дефицит калорий.
        # Можно выбрать дефицит в пределах 10-20% от TDEE.
        calorie_deficit = 0.1 * tdee
        max_calories = tdee - calorie_deficit
        min_calories = tdee - 2 * calorie_deficit  # Больший дефицит для более быстрого похудения
    elif goal in ['BUILD_MUSCLE', 'MUSCLE_STRENGHT']:
        # Чтобы нарастить мышцы, создаем положительный калорийный баланс.
        # Можно увеличить TDEE на 5-10% для наращивания мышц.
        calorie_surplus = 0.05 * tdee
        min_calories = tdee + calorie_surplus
        max_calories = tdee + 2 * calorie_surplus  # Больший баланс для более интенсивного наращивания
    else:
        min_calories = 0
        max_calories = 0

    return int(round(min_calories)), int(round(max_calories))

if __name__ == '__main__':
    bmr = calculate_bmr_mifflin(106, 173, 23, 'male')
    print('BMR', bmr)
    tdee = calculate_tdee(bmr, 1.2)
    print('TDEE', tdee)
    print('calories', calculate_calorie_range(tdee, 'MUSCLE_STRENGHT'))