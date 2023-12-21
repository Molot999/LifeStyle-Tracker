from typing import List
import dbconnection as db


def get_analyze_str(user_id, total_calories, total_protein, total_fat, total_carbohydrate):
    if db.get_user_body_profile(user_id):
        if db.check_is_user_diet_macros_filled(user_id):
            user_diet_macros = db.get_user_diet_macros(user_id)

            calories_min, calories_max  = str(user_diet_macros.calories_range).split('-')
            calories_min = int(calories_min)
            calories_max = int(calories_max)
            calories_analyzing = get_calories_analyzing(total_calories, calories_min, calories_max)

            protein_goal = user_diet_macros.protein_g
            protein_analyzing = get_protein_analyzing(total_protein, protein_goal)

            fat_goal = user_diet_macros.fat_g
            fat_analyzing = get_fat_analyzing(total_fat, fat_goal)

            carbohydrate_goal = user_diet_macros.carbohydrate_g
            carbohydrate_analyzing = get_carbohydrate_analyzing(total_carbohydrate, carbohydrate_goal)
            
            return calories_analyzing + protein_analyzing + fat_analyzing + carbohydrate_analyzing
        else:
            return '\nЧтобы эффективно отслеживать свое питание вам следует установить цели по калориям, белкам, жирам и углеводам. Это можно сделать, нажав на кнопку "Настройки" ниже'
    else:
        return '\nДля получения рекоммендаций по питанию и тренировкам вам следует заполнить профиль физических данных (пол, возраст, вес и т.д). Это можно сделать, нажав на кнопку "Профиль" ниже'
    
def get_calories_analyzing(total_calories, calories_min, calories_max):
    if total_calories < calories_min:
        return f"\nНе хватает {int(calories_min - total_calories)} калорий."
    elif total_calories > calories_max:
        return  f"\nВы превысили норму на {int(total_calories - calories_max)} калорий."
    else:
        return  "\nВаш калораж в пределах нормы 👍"


def get_protein_analyzing(total_protein, protein_goal):
    protein_min = int(protein_goal*0.9)
    protein_max = int(protein_goal*1.1)
    if total_protein < protein_min:
        return f"\nНе хватает {int(protein_min - total_protein)} г. белков"
    elif total_protein > protein_max:
        return  f"\nВы превысили норму на {int(total_protein - protein_max)} г. белков"
    else:
        return  "\nБелок в пределах нормы 👍"
    
def get_fat_analyzing(total_fat, fat_goal):
    fat_min = int(fat_goal*0.9)
    fat_max = int(fat_goal*1.1)
    if total_fat < fat_min:
        return  f"\nНе хватает {int(fat_min - total_fat)} г. жиров"
    elif total_fat > fat_max:
        return f"\nВы превысили норму на {int(total_fat - fat_max)} г. жиров"
    else:
        return  "\nЖиры в пределах нормы 👍"
    
def get_carbohydrate_analyzing(total_carbohydrate, carbohydrate_goal):
    carbohydrate_min = int(carbohydrate_goal*0.9)
    carbohydrate_max = int(carbohydrate_goal*1.1)
    if total_carbohydrate < carbohydrate_min:
        return f"\nНе хватает {int(carbohydrate_min - total_carbohydrate)} г. углеводов"
    elif total_carbohydrate > carbohydrate_max:
        return f"\nВы превысили норму на {int(total_carbohydrate - carbohydrate_max)} г. углеводов"
    else:
        return "\nУглеводы в пределах нормы 👍"

if __name__ == '__main__':
    print(get_analyze_str(1, 754, 50, 30, 71))