from dbmanager import DBManager
import datetime
from workout_utils import Workout, AvailableExercise, WorkoutExercise, ExerciseSet
from user_body_profile_classes import UserBodyProfile
from nutritionix_utils import NutritionixNutrient
from nutrition_utils import Product
from meal_diary_utils import UserMealDiaryProduct
from typing import List
from user_diet_macros_utils import UserDietMacros
from user_weight_diaries_utils import UserWeightDiaryEntry
from user_body_measurements_utils import BodyMeasurements
from receipts_utils import Receipt, ReceiptIngredient, ReceiptStep
from user_foods_utils import UserFood

def get_user_timezone(user_id):
    with DBManager() as cursor:
        cursor.execute("SELECT timezone_UTC FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()[0]

def set_user_timezone(user_id, timezone):
    with DBManager() as cursor:
        cursor.execute("UPDATE users SET timezone_UTC = ? WHERE id = ?", (timezone, user_id))

def get_user_chat_ids():
    with DBManager() as cursor:
        cursor.execute("SELECT chat_id FROM users")
        return [chat_id_tuple[0] for chat_id_tuple in cursor.fetchall()]

def check_user_exists(chat_id) -> bool:
    with DBManager() as cursor:
        cursor.execute("SELECT COUNT(*) FROM users WHERE chat_id = ?", (chat_id,))
        result = cursor.fetchone()[0]
        return result > 0

def add_user(username, chat_id, name=None) -> None:
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
        existing_user = cursor.fetchone()
        if existing_user is None:
            # Если запись не существует
            with DBManager() as cursor:
                cursor.execute("INSERT INTO users (username, chat_id, name) VALUES (?, ?, ?)", (username, chat_id, name))

def get_user_test_period_status(chat_id) -> bool:
    with DBManager() as cursor:
        cursor.execute("SELECT used_test_period FROM users WHERE chat_id = ?", (chat_id,))
        result = cursor.fetchone()
        if result is None:
            return None
        result = result[0]
        return result == 1

def update_user_test_period_status(chat_id,  used_test_period) -> None:
    used_test_period = 1 if used_test_period is True else 0
    with DBManager() as cursor:
        cursor.execute("UPDATE users SET used_test_period = ? WHERE chat_id = ?", (used_test_period, chat_id))

def get_name(chat_id) -> str:
    with DBManager() as cursor:
        cursor.execute("SELECT name FROM users WHERE chat_id = ?", (chat_id,))
        name_tuple = cursor.fetchone()
        return name_tuple[0] if name_tuple is not None else None

def get_subscription_data(id):
    with DBManager() as cursor:
        cursor.execute("SELECT period_days FROM available_subscription WHERE id = ?", (id,))
        name_tuple = cursor.fetchone()
        return name_tuple[0] if name_tuple is not None else None

def add_user_subscription(chat_id, subscription_id=None, period_days=None) -> str:
    if subscription_id is not None:
        subscription_info = get_subscription_info(subscription_id)
        subscription_period_days = subscription_info['period_days']
    else:
        subscription_period_days = period_days
        
    with DBManager() as cursor:
        cursor.execute("SELECT end_date FROM user_subscriptions WHERE chat_id=?", (chat_id,))
        subscription_tuple = cursor.fetchone()
        if subscription_tuple is None:
            # Получаем текущую дату и время
            current_datetime = datetime.datetime.now()
            end_date = current_datetime + datetime.timedelta(days=subscription_period_days)
            with DBManager() as cursor:
                cursor.execute("INSERT INTO user_subscriptions (chat_id, end_date) VALUES (?, ?)", (chat_id, end_date))
        else:
            last_end_datetime = subscription_tuple[0]
            date_format = "%Y-%m-%d %H:%M:%S.%f"
            last_end_datetime = datetime.datetime.strptime(last_end_datetime, date_format)
            # Получаем текущее время
            current_datetime = datetime.datetime.now()

            # Если подписка уже закончилась
            if current_datetime > last_end_datetime:
                new_end_date = datetime.datetime.now() + datetime.timedelta(days=subscription_period_days)
            # Если подписка еще действует
            else:
                new_end_date = last_end_datetime + datetime.timedelta(days=subscription_period_days)

            with DBManager() as cursor:
                cursor.execute("UPDATE user_subscriptions SET end_date = ? WHERE chat_id = ?", (new_end_date, chat_id))

def get_user_subscription_info(chat_id) -> str:
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM user_subscriptions WHERE chat_id = ?", (chat_id,))
        if subscription_info_tuple := cursor.fetchone():
            end_date = subscription_info_tuple[2]
            # Формат даты соответствует исходной строке
            date_format = "%Y-%m-%d %H:%M:%S.%f"
            return (subscription_info_tuple[0], datetime.datetime.strptime(end_date, date_format))
        else:
            None

def get_subscription_info(subscription_id):
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM available_subscriptions WHERE id = ?", (subscription_id,))
        subscription_tuple = cursor.fetchone()
        if subscription_tuple is not None:
            return {'id': subscription_tuple[0],
                    'is_active': subscription_tuple[1],
                    'period_days': subscription_tuple[2],
                    'price': subscription_tuple[3]}
        else:
            return None

def add_available_subscription(period_days, price):
    with DBManager() as cursor:
        cursor.execute("INSERT INTO available_subscriptions (period_days, price) VALUES (?, ?)", (period_days, price))

def add_promocode(promocode, discounted_percent):
    with DBManager() as cursor:
        cursor.execute("INSERT INTO promocodes (promocode, discounted_percent) VALUES (?, ?)", (promocode, discounted_percent))

def get_promocode_discounted_percent(promocode):
    with DBManager() as cursor:
        cursor.execute("SELECT discounted_percent FROM promocodes WHERE promocode = ?", (promocode,))
        promocode_info_tuple = cursor.fetchone()
        return promocode_info_tuple[0] if promocode_info_tuple is not None else None

def get_available_subscriptions():
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM available_subscriptions")
        return cursor.fetchall()
    
def get_available_subscription(id):
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM available_subscriptions WHERE id = ?", (id,))
        return cursor.fetchone()

def get_username(chat_id):
    with DBManager() as cursor:
        cursor.execute("SELECT username FROM users WHERE chat_id = ?", (chat_id,))
        promocode_info_tuple = cursor.fetchone()
        return promocode_info_tuple[0] if promocode_info_tuple is not None else None

def get_user_id(chat_id):
    with DBManager() as cursor:
        cursor.execute("SELECT id FROM users WHERE chat_id = ?", (chat_id,))
        user_data_tuple = cursor.fetchone()
        return user_data_tuple[0] if user_data_tuple is not None else None
    
def get_user_workouts(chat_id) -> List[Workout]:
    with DBManager() as cursor:
        cursor.execute("SELECT id, start_date, end_date, volume, intensity, duration_mins FROM user_workouts WHERE chat_id = ?", (chat_id,))
        if user_workouts_data := cursor.fetchall():
            return [Workout(*workout_data) for workout_data in user_workouts_data]
        
def get_user_workout(workout_id) -> Workout:
    with DBManager() as cursor:
        cursor.execute("SELECT id, start_date, end_date, volume, intensity, duration_mins FROM user_workouts WHERE id = ?", (workout_id,))
        if user_workouts_data := cursor.fetchone():
            return Workout(*user_workouts_data)

def add_user_workout(chat_id, start_date, end_date=None) -> int:
    with DBManager() as cursor:
        cursor.execute("INSERT INTO user_workouts (chat_id, start_date, end_date) VALUES (?, ?, ?)",
                    (chat_id,
                    start_date,
                    end_date))
        return cursor.lastrowid

def update_user_workout(started_workout_id, start_date=None, end_date=None, intensity=None, volume=None, duration_mins=None):
    with DBManager() as cursor:
        # Формирование запроса с учетом переданных параметров
        query = "UPDATE user_workouts SET"
        update_values = []

        if start_date is not None:
            query += " start_date = ?,"
            update_values.append(start_date)
        if end_date is not None:
            query += " end_date = ?,"
            update_values.append(end_date)
        if intensity is not None:
            query += " intensity = ?,"
            update_values.append(intensity)
        if volume is not None:
            query += " volume = ?,"
            update_values.append(volume)
        if duration_mins is not None:
            query += " duration_mins = ?,"
            update_values.append(duration_mins)

        query = query.rstrip(',') + " WHERE id = ?"
        update_values.append(started_workout_id)

        # Выполнение запроса
        cursor.execute(query, update_values)

def delete_user_workout(started_workout_id):
    with DBManager() as cursor:
        cursor.execute("DELETE FROM user_workouts WHERE id = ?",
                    (started_workout_id,))   

def get_workout_exercises(workout_id) -> List[WorkoutExercise]:
    with DBManager() as cursor:
        cursor.execute("SELECT id, workout_id, exercise_id, start_date, end_date FROM workout_exercises WHERE workout_id = ?", (workout_id,))
        if workout_exercises_data := cursor.fetchall():
            return [WorkoutExercise(*workout_exercise_data) for workout_exercise_data in workout_exercises_data]

def add_workout_exercise(workout_id, exercise_id, start_date, end_date=None) -> int:
    with DBManager() as cursor:
        cursor.execute("INSERT INTO workout_exercises (workout_id, exercise_id, start_date, end_date) VALUES (?, ?, ?, ?)",
                    (workout_id,
                    exercise_id,
                    start_date,
                    end_date))
    return cursor.lastrowid

def update_workout_exercise(started_exercise_table_id, start_date=None, end_date=None):
    with DBManager() as cursor:
        # Формирование запроса с учетом переданных параметров
        query = "UPDATE workout_exercises SET"
        update_values = []

        if start_date is not None:
            query += " start_date = ?,"
            update_values.append(start_date)
        if end_date is not None:
            query += " end_date = ?,"
            update_values.append(end_date)

        query = query.rstrip(',') + " WHERE id = ?"
        update_values.append(started_exercise_table_id)

        # Выполнение запроса
        cursor.execute(query, update_values)

def delete_workout_exercise(started_exercise_table_id):
    with DBManager() as cursor:
        cursor.execute("DELETE FROM workout_exercises WHERE id = ?",
                    (started_exercise_table_id,))

def get_exercise_sets(exercise_table_id) -> list[ExerciseSet]:
    with DBManager() as cursor:
        cursor.execute("SELECT id, exercise_table_id, start_date, end_date, rep_count, equipment_weight FROM exercise_sets WHERE exercise_table_id = ?", (exercise_table_id,))
        if exercise_sets_data := cursor.fetchall():
            return [ExerciseSet(*exercise_set_data) for exercise_set_data in exercise_sets_data]

def add_exercise_set(exercise_table_id, start_date, equipment_weight, rep_count=None, end_date=None) -> int:
    with DBManager() as cursor:
        cursor.execute("INSERT INTO exercise_sets (exercise_table_id, start_date, equipment_weight, rep_count, end_date) VALUES (?, ?, ?, ?, ?)",
                    (exercise_table_id,
                    start_date,
                    equipment_weight,
                    rep_count,
                    end_date))
    return cursor.lastrowid

def update_exercise_set(started_set_table_id, start_date=None, end_date=None, equipment_weight=None, rep_count=None):
    with DBManager() as cursor:
        # Формирование запроса с учетом переданных параметров
        query = "UPDATE exercise_sets SET"
        update_values = []

        if start_date is not None:
            query += " start_date = ?,"
            update_values.append(start_date)
        if equipment_weight is not None:
            query += " equipment_weight = ?,"
            update_values.append(equipment_weight)
        if rep_count is not None:
            query += " rep_count = ?,"
            update_values.append(rep_count)
        if end_date is not None:
            query += " end_date = ?,"
            update_values.append(end_date)

        query = query.rstrip(',') + " WHERE id = ?"
        update_values.append(started_set_table_id)

        # Выполнение запроса
        cursor.execute(query, update_values)

def delete_exercise_set(id):
    with DBManager() as cursor:
        cursor.execute("DELETE FROM exercise_sets WHERE id = ?", (id,))

def add_available_exercise(title, muscle_group, additional_muscles, ex_type, ex_kind, equipment, difficulty_level, url) -> int:
    with DBManager() as cursor:
        cursor.execute("INSERT INTO available_exercises (title, muscle_group, additional_muscles, ex_type, ex_kind, equipment, difficulty_level, url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (title,
                        muscle_group,
                        additional_muscles,
                        ex_type,
                        ex_kind,
                        equipment,
                        difficulty_level,
                        url))
        return cursor.lastrowid

def find_available_exercise(query):
    query = f'%{str(query)}%'
    print('query', query)
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM available_exercises WHERE LOWER(title) LIKE ?", (query,))
        return cursor.fetchall()

def get_available_exercise(available_exercise_id):
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM available_exercises WHERE id = ?", (available_exercise_id,))
        if available_exercise_tuple := cursor.fetchone():
            return AvailableExercise(*available_exercise_tuple)

def add_available_exercise_photo(exercise_id, image_url, sex):
    with DBManager() as cursor:
        cursor.execute("INSERT INTO exercise_photos (exercise_id, image_url, sex) VALUES (?, ?, ?)",
                        (exercise_id,
                        image_url,
                        sex))

def get_available_exercise_photo_urls(exercise_id, sex='male'):
    with DBManager() as cursor:
        cursor.execute("SELECT image_url FROM exercise_photos WHERE exercise_id = ? and sex = ?", (exercise_id, sex))
        photo_tuples = cursor.fetchall()
        return [photo_tuple[0] for photo_tuple in photo_tuples]

def add_user_body_profile(user_body_profile:UserBodyProfile):
    attributes = vars(user_body_profile)
    print(f"Class: {user_body_profile.__class__.__name__}")
    for attribute, value in attributes.items():
        print(f"{attribute}: {value}")

    with DBManager() as cursor:
        # Проверяем наличие записи с указанным user_id
        cursor.execute('SELECT COUNT(*) FROM user_body_profile WHERE user_id = ?', (user_body_profile.user_id,))
        count = cursor.fetchone()[0]

    if count == 0:
        with DBManager() as cursor:
            cursor.execute("""INSERT INTO user_body_profile
                        (user_id, birth_date, height, weight, sex, physical_activity_level, BMI, BMR, TDEE, goal) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            user_body_profile.user_id,
            user_body_profile.birth_date,
            user_body_profile.height,
            user_body_profile.weight,
            user_body_profile.sex,
            user_body_profile.physical_activity_level,
            user_body_profile.BMI,
            user_body_profile.BMR,
            user_body_profile.TDEE,
            user_body_profile.goal
            ))

def get_user_body_profile(user_id) -> UserBodyProfile:
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM user_body_profile WHERE user_id = ?", (user_id,))
        if available_exercise_tuple := cursor.fetchone():
            return UserBodyProfile(*available_exercise_tuple)
        
def check_user_body_profile_exists(user_id) -> bool:
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM user_body_profile WHERE user_id = ?", (user_id,))
        return bool(cursor.fetchone())

def update_user_body_profile(user_id, birth_date=None, height=None, weight=None, sex=None, physical_activity_level=None,
                            BMI=None, BMR=None, TDEE=None, goal=None):
    with DBManager() as cursor:
        # Формирование запроса с учетом переданных параметров
        query = "UPDATE user_body_profile SET"
        update_values = []

        if birth_date is not None:
            query += " birth_date = ?,"
            update_values.append(birth_date)
        if height is not None:
            query += " height = ?,"
            update_values.append(height)
        if weight is not None:
            query += " weight = ?,"
            update_values.append(weight)
        if sex is not None:
            query += " sex = ?,"
            update_values.append(sex)
        if physical_activity_level is not None:
            query += " physical_activity_level = ?,"
            update_values.append(physical_activity_level)
        if BMI is not None:
            query += " BMI = ?,"
            update_values.append(BMI)
        if BMR is not None:
            query += " BMR = ?,"
            update_values.append(BMR)
        if TDEE is not None:
            query += " TDEE = ?,"
            update_values.append(TDEE)
        if goal is not None:
            query += " goal = ?,"
            update_values.append(goal)

        query = query.rstrip(',') + " WHERE user_id = ?"
        update_values.append(user_id)

        # Выполнение запроса
        cursor.execute(query, update_values)

def delete_table(table_name):
    with DBManager() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

def get_nutritionix_nutrient_info(attr_id, value):
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM nutritionix_nutrients WHERE attr_id = ?", (attr_id,))
        if nutritionix_nutrients_tuple := cursor.fetchone():
            result = NutritionixNutrient(*nutritionix_nutrients_tuple)
            result.value = value
            return result

def add_product(barcode, brand_name, name, weight_g, calories_100_g, fat_g,
                                satured_fat_g, protein_g, carbohydrate_g, sugar_g, cellulose_g, salt_g):
    with DBManager() as cursor:
        # Проверяем, существует ли запись с таким barcode
        cursor.execute("SELECT id FROM products WHERE barcode=?", (barcode,))
        existing_id = cursor.fetchone()

    if existing_id is None:
        with DBManager() as cursor:
            # Если записи с таким barcode нет, то добавляем новую запись
            cursor.execute("""
                INSERT INTO products (barcode, brand_name, name, weight_g, calories_100_g, fat_g,
                                    satured_fat_g, protein_g, carbohydrate_g, sugar_g, cellulose_g, salt_g)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (barcode, brand_name, name, weight_g, calories_100_g, fat_g,
                satured_fat_g, protein_g, carbohydrate_g, sugar_g, cellulose_g, salt_g))
    else:
        # Если запись с таким barcode уже существует, выводим текст
        print("Запись с таким barcode уже существует.")

def get_product(barcode) -> Product:
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM products WHERE barcode = ?", (barcode,))
        if product_tuple := cursor.fetchone():
            return Product(*product_tuple)

def add_food_diary_entry(user_id, food_name, brand_name, serving_qty, serving_weight_grams, calories, total_fat, saturated_fat, cholesterol,
                        total_carbohydrate, dietary_fiber, sugars, protein, potassium, p, full_nutrients, datetime):
    with DBManager() as cursor:
            # Если записи с таким barcode нет, то добавляем новую запись
            cursor.execute('''
                INSERT INTO user_food_diaries(
                user_id,
                food_name,
                brand_name,
                serving_qty,
                serving_weight_grams,
                calories,
                total_fat,
                saturated_fat,
                cholesterol,
                total_carbohydrate,
                dietary_fiber,
                sugars,
                protein,
                potassium,
                p,
                full_nutrients,
                datetime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (user_id,
                food_name,
                brand_name,
                serving_qty,
                serving_weight_grams,
                calories,
                total_fat,
                saturated_fat,
                cholesterol,
                total_carbohydrate,
                dietary_fiber,
                sugars,
                protein,
                potassium,
                p,
                full_nutrients,
                datetime))

def delete_food_diary_entry(food_id):
    with DBManager() as cursor:
        cursor.execute("DELETE FROM user_food_diaries WHERE id = ?", (food_id,))

def get_user_meal_diary_periods(user_id):
    with DBManager() as cursor:
        cursor.execute("SELECT datetime FROM user_food_diaries WHERE user_id = ?", (user_id,))
        if meal_diary_periods_tuple := cursor.fetchall():
            return [meal_diary_period[0] for meal_diary_period in meal_diary_periods_tuple]

def get_user_meal_period_data(user_id, period) -> List[UserMealDiaryProduct]:
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM user_food_diaries WHERE datetime LIKE ? AND user_id = ?", ('%' + period + '%', user_id))
        if food_diary_tuple := cursor.fetchall():
            return [UserMealDiaryProduct(*food) for food in food_diary_tuple]

def check_user_diet_macros_exists(user_id):
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM user_diet_macros WHERE user_id = ?", (user_id,))
        return bool(cursor.fetchone())

def check_is_user_diet_macros_filled(user_id):
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM user_diet_macros WHERE user_id = ?", (user_id,))
        if user_diet_macros_tuple := cursor.fetchone():
            return all(diet_macros is not None and len(str(diet_macros)) > 0 for diet_macros in user_diet_macros_tuple)
        else:
            return False

def get_user_diet_macros(user_id) -> UserDietMacros:
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM user_diet_macros WHERE user_id = ?", (user_id,))
        if user_diet_macros_tuple := cursor.fetchone():
            return UserDietMacros(*user_diet_macros_tuple)

def set_user_diet_macros(user_id, calories_range=None, protein_g=None, fat_g=None, carbohydrate_g=None):
    with DBManager() as cursor:
        cursor.execute("INSERT INTO user_diet_macros(user_id, calories_range, protein_g, fat_g, carbohydrate_g) VALUES(?, ?, ?, ?, ?)",
                    (user_id, calories_range, protein_g, fat_g, carbohydrate_g))

def update_user_diet_macros(user_id, calories_range=None, protein_g=None, fat_g=None, carbohydrate_g=None):
    with DBManager() as cursor:
        # Формирование запроса с учетом переданных параметров
        query = "UPDATE user_diet_macros SET"
        update_values = []
        if calories_range is not None:
            query += " calories_range = ?,"
            update_values.append(calories_range)
        if protein_g is not None:
            query += " protein_g = ?,"
            update_values.append(protein_g)
        if fat_g is not None:
            query += " fat_g = ?,"
            update_values.append(fat_g)
        if carbohydrate_g is not None:
            query += " carbohydrate_g = ?,"
            update_values.append(carbohydrate_g)

        query = query.rstrip(',') + " WHERE user_id = ?"
        update_values.append(user_id)

        # Выполнение запроса
        cursor.execute(query, update_values)

def get_user_food_diary_full_nutrients(user_id, date)-> List:
    with DBManager() as cursor:
        cursor.execute("SELECT full_nutrients FROM user_food_diaries WHERE user_id = ? AND datetime LIKE ?", (user_id, f'%{date}%'))
        if user_food_diary_full_nutrients_tuple := cursor.fetchall():
            return user_food_diary_full_nutrients_tuple

def get_user_weight_diary(user_id) -> List[UserWeightDiaryEntry]:
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM user_weight_diaries WHERE user_id = ?", (user_id,))
        if user_weight_diary_tuple := cursor.fetchall():
            return [UserWeightDiaryEntry(*user_weight_diary) for user_weight_diary in user_weight_diary_tuple]
        
def get_user_weight_diary_entry(id) -> UserWeightDiaryEntry:
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM user_weight_diaries WHERE id = ?", (id,))
        if user_weight_diary_entry_tuple := cursor.fetchone():
            return UserWeightDiaryEntry(*user_weight_diary_entry_tuple)

def add_user_weight_diary_entry(user_id, weight, date):
    with DBManager() as cursor:
        cursor.execute("INSERT INTO user_weight_diaries(user_id, weight, datetime) VALUES(?, ?, ?)",
                    (user_id, weight, date))
        
def delete_user_weight_diary_entry(weight_diary_entry_id):
    with DBManager() as cursor:
        cursor.execute("DELETE FROM user_weight_diaries WHERE id = ?",
                    (weight_diary_entry_id,)) 

def add_user_body_measurements(user_id, shoulders, forearms, biceps, chest, waist, thighs, calves, neck, datetime_str):
    with DBManager() as cursor:
        cursor.execute("INSERT INTO user_body_measurements(user_id, shoulders, forearms, biceps, chest, waist, thighs, calves, neck, datetime) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (user_id, shoulders, forearms, biceps, chest, waist, thighs, calves, neck, datetime_str))

def get_user_body_measurements(user_id) -> List[BodyMeasurements]:
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM user_body_measurements WHERE user_id = ?", (user_id,))
        if user_body_measurements_tuple := cursor.fetchall():
            return [BodyMeasurements(*user_body_measurement) for user_body_measurement in user_body_measurements_tuple]
        
def delete_user_body_measurements_entry(body_measurements_id):
    with DBManager() as cursor:
        cursor.execute("DELETE FROM user_body_measurements WHERE id = ?",
                    (body_measurements_id,)) 

def add_receipt(receipt:Receipt) -> int:
    # SQL-запрос для добавления данных в таблицу receipts
    insert_sql = '''
INSERT INTO receipts (title, img_url, description, category_1, category_2, category_3, calories_100g, proteins_100g, fats_100g, carbohydrates_100g, url)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''
    # Значения для добавления
    values = (receipt.title, receipt.img_url ,receipt.description, receipt.category_1, receipt.category_2,
            receipt.category_3, receipt.calories_100g, receipt.proteins_100g,
            receipt.fats_100g, receipt.carbohydrates_100g, receipt.url)
    with DBManager() as cursor:
        cursor.execute(insert_sql, values)
        return cursor.lastrowid

def add_receipt_ingredients(receipt_ingredients:List[ReceiptIngredient]) -> None:
    # SQL-запрос для добавления данных в таблицу receipts
    insert_sql = '''
INSERT INTO receipt_ingredients (receipt_id, title, weight)
VALUES (?, ?, ?)
'''
    with DBManager() as cursor:
        for receipt_ingredient in receipt_ingredients:
            # Значения для добавления
            values = (receipt_ingredient.receipt_id, receipt_ingredient.title, receipt_ingredient.weight)
            cursor.execute(insert_sql, values)

def add_receipt_ingredients(receipt_ingredients:List[ReceiptIngredient]) -> None:
    # SQL-запрос для добавления данных в таблицу receipts
    insert_sql = '''
INSERT INTO receipt_ingredients (receipt_id, title, weight)
VALUES (?, ?, ?)
'''
    with DBManager() as cursor:
        for receipt_ingredient in receipt_ingredients:
            # Значения для добавления
            values = (receipt_ingredient.receipt_id, receipt_ingredient.title, receipt_ingredient.weight)
            cursor.execute(insert_sql, values)

def add_receipt_steps(receipt_steps:List[ReceiptStep]) -> None:
    # SQL-запрос для добавления данных в таблицу receipts
    insert_sql = '''
INSERT INTO receipt_steps (receipt_id, number, img_url, description)
VALUES (?, ?, ?, ?)
'''
    with DBManager() as cursor:
        for receipt_step in receipt_steps:
            # Значения для добавления
            values = (receipt_step.receipt_id, receipt_step.number, receipt_step.img_url, receipt_step.description)
            cursor.execute(insert_sql, values)

def get_receipt(receipt_id) -> Receipt:
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM receipts WHERE id = ? LIMIT 1", (receipt_id,))
        if receipt_tuple := cursor.fetchone():
            return Receipt(*receipt_tuple)

def get_random_receipt() -> Receipt:
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM receipts ORDER BY RANDOM() LIMIT 1")
        if receipt_tuple := cursor.fetchone():
            return Receipt(*receipt_tuple)

def get_receipt_ingredients(receipt_id) -> List[ReceiptIngredient]:
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM receipt_ingredients WHERE receipt_id = ?", (receipt_id,))
        if receipt_ingredients_tuple := cursor.fetchall():
            print(receipt_ingredients_tuple)
            return [ReceiptIngredient(*receipt_ingredient) for receipt_ingredient in receipt_ingredients_tuple]

def add_user_food(user_food:UserFood):
    sql_query = '''INSERT INTO user_foods (user_id, barcode, title, group_name, weight, one_piece_weight, 
                                    calories, fat, protein, carbohydrate, full_nutrients, is_animal_protein, 
                                    is_unsaturated_fats, is_complex_carbohydrates)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    data = (user_food.user_id, user_food.barcode, user_food.title, user_food.group_name,
            user_food.weight, user_food.one_piece_weight, user_food.calories, user_food.fat,
            user_food.protein, user_food.carbohydrate, user_food.full_nutrients,
            user_food.is_animal_protein, user_food.is_unsaturated_fats, user_food.is_complex_carbohydrates)
    with DBManager() as cursor:
        cursor.execute(sql_query, data)

def search_user_foods(user_id, query):
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM user_foods WHERE title LIKE ? and user_id = ?", (f'%{query}%', user_id))
        if user_foods_tuple := cursor.fetchall():
            return [UserFood(*user_food) for user_food in user_foods_tuple]

def get_user_foods(user_id):
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM user_foods WHERE user_id = ?", (user_id,))
        if user_foods_tuple := cursor.fetchall():
            return [UserFood(*user_food) for user_food in user_foods_tuple]
        
def is_user_foods_added(user_id):
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM user_foods WHERE user_id = ?", (user_id,))
        if user_food_tuple := cursor.fetchone():
            return bool(user_food_tuple)
        
def delete_user_foods(user_id):
    with DBManager() as cursor:
        cursor.execute("DELETE FROM user_foods WHERE user_id = ?", (user_id,))

def add_nutritionix_cache_entry(query, query_hash, data, entry_date):
    with DBManager() as cursor:
        cursor.execute("INSERT INTO nutritionix_cache (query, query_hash, data, entry_date) VALUES (?, ?, ?, ?)", (query, query_hash, data, entry_date))
        return cursor.lastrowid
        
def get_nutritionix_cache_entries():
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM nutritionix_cache")
        return cursor.fetchall()
    
def get_nutritionix_cache_entry_by_hash(query_hash):
    with DBManager() as cursor:
        cursor.execute("SELECT query, query_hash, data, entry_date FROM nutritionix_cache WHERE query_hash = ?", (query_hash,))
        return cursor.fetchone()

def get_app_state_info(app_version:str):
    with DBManager() as cursor:
        cursor.execute("SELECT * FROM app_state WHERE app_version = ?", (app_version,))
        return cursor.fetchone()
    
def add_app_state_info(app_version:str):
    with DBManager() as cursor:
        cursor.execute("INSERT INTO app_state (app_version) VALUES (?)", (app_version,))

def update_app_state_info(app_version:str, are_users_informed:bool):
    with DBManager() as cursor:
        are_users_informed = 1 if are_users_informed else 0
        cursor.execute("UPDATE app_state SET are_users_informed = ? WHERE app_version = ?", (are_users_informed, app_version))

def add_payment(bill_label, payment_url, period):
    with DBManager() as cursor:
        cursor.execute("INSERT INTO payments (bill_label, payment_url, period) VALUES (?, ?, ?)", (bill_label, payment_url, period))

def get_payment(bill_label):
    with DBManager() as cursor:
        cursor.execute("SELECT period FROM payments WHERE bill_label = ?", (bill_label,))
        return payment[0] if (payment := cursor.fetchone()) else None 

def try_clear_user_data(chat_id, user_id):
    try:
        with DBManager() as cursor:
            cursor.execute("DELETE FROM users WHERE chat_id = ?", (chat_id,))
            cursor.execute("DELETE FROM user_food_diaries WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM user_diet_macros WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM user_body_profile WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM user_weight_diaries WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM user_workouts WHERE chat_id = ?", (chat_id,))
            cursor.execute("DELETE FROM user_foods WHERE user_id = ?", (user_id,))
        return True
    except Exception as e:
        print('clear_user_data():', e)
        return False
    
def try_clear_user_subscription(chat_id):
    try:
        with DBManager() as cursor:
            cursor.execute("DELETE FROM user_subscriptions WHERE chat_id = ?", (chat_id,))
        return True
    except Exception as e:
        print('try_clear_user_subscription():', e)
        return False

def test():
    with DBManager() as cursor:
        cursor.execute("UPDATE user_subscriptions SET end_date = ? WHERE chat_id = ?", ('2053-09-21 00:00:00.000000', '6628340927'))

# sourcery skip: remove-redundant-if
if __name__ == '__main__':
    pass