import sqlite3
from dbmanager import db_name


def initialize() -> None:
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # Создание таблицы
    cur.execute(
        """CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                trainer_id INTEGER DEFAULT 0,
                username TEXT,
                name TEXT,
                chat_id INTEGER,
                used_test_period INTEGER DEFAULT 0)"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS user_subscriptions
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                end_date TEXT)"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS user_workouts
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                start_date TEXT,
                volume INTEGER,
                intensity INTEGER,
                duration_mins INTEGER,
                end_date TEXT)"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS workout_exercises
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_id INTEGER,
                exercise_id INTEGER,
                start_date TEXT,
                end_date TEXT,
                FOREIGN KEY (workout_id) REFERENCES user_workouts (id),
                FOREIGN KEY (exercise_id) REFERENCES available_subscriptions (id))"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS exercise_sets
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercise_table_id INTEGER,
                start_date TEXT,
                end_date TEXT,
                rep_count INTEGER,
                equipment_weight REAL,
                FOREIGN KEY (exercise_table_id) REFERENCES workout_exercises (id))"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS available_subscriptions
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                period_days INTEGER,
                price INTEGER)"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS available_exercises
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                muscle_group TEXT,
                additional_muscles TEXT,
                ex_type TEXT,
                ex_kind TEXT,
                equipment TEXT,
                difficulty_level TEXT,
                done_num INTEGER DEFAULT 0,
                view_num INTEGER DEFAULT 0,
                url TEXT)"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS exercise_photos (
                id INTEGER PRIMARY KEY,
                exercise_id INTEGER,
                image_url TEXT,
                sex TEXT,
                FOREIGN KEY (exercise_id) REFERENCES available_exercises (id))"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS user_weight_diaries (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                weight REAL,
                datetime TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id))"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS user_body_measurements (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                shoulders REAL,
                forearms REAL,
                biceps REAL,
                chest REAL,
                waist REAL,
                thighs REAL,
                calves REAL,
                neck REAL,
                datetime TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id))"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS user_body_profile (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                birth_date TEXT,
                height INTEGER,
                weight REAL,
                sex TEXT,
                physical_activity_level INTEGER,
                BMI REAL,
                BMR INTEGER,
                TDEE INTEGER,
                goal TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id))"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                barcode INTEGER,
                brand_name TEXT,
                name TEXT,
                weight_g INTEGER,
                calories_100_g INTEGER,
                fat_g REAL,
                satured_fat_g REAL,
                protein_g REAL,
                carbohydrate_g REAL,
                sugar_g REAL,
                cellulose_g REAL,
                salt_g REAL)"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS user_food_diaries (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                food_name TEXT,
                brand_name TEXT,
                serving_qty REAL,
                serving_weight_grams REAL,
                calories REAL,
                total_fat REAL,
                saturated_fat REAL,
                cholesterol REAL,
                total_carbohydrate REAL,
                dietary_fiber REAL,
                sugars REAL,
                protein REAL,
                potassium REAL,
                p REAL,
                full_nutrients TEXT,
                datetime TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id))"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS user_diet_macros (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            calories_range TEXT,
            protein_g INTEGER,
            fat_g INTEGER,
            carbohydrate_g INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id))"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS receipts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        img_url TEXT,
        description TEXT,
        category_1 TEXT,
        category_2 TEXT,
        category_3 TEXT,
        calories_100g REAL,
        proteins_100g REAL,
        fats_100g REAL,
        carbohydrates_100g REAL,
        url TEXT)"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS receipt_ingredients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receipt_id INTEGER,
        title TEXT,
        weight TEXT,
        FOREIGN KEY (receipt_id) REFERENCES receipts (id))"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS receipt_steps(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receipt_id INTEGER,
        number INTEGER,
        img_url TEXT,
        description TEXT,
        FOREIGN KEY (receipt_id) REFERENCES receipts (id))"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS user_foods (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            barcode INTEGER,
            title TEXT,
            group_name TEXT,
            weight REAL,
            one_piece_weight REAL,
            calories REAL,
            fat REAL,
            protein REAL,
            carbohydrate REAL,
            full_nutrients TEXT,
            is_animal_protein INTEGER,
            is_unsaturated_fats INTEGER,
            is_complex_carbohydrates INTEGER)"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS nutritionix_cache (
            id INTEGER PRIMARY KEY,
            query TEXT,
            query_hash TEXT,
            data TEXT,
            entry_date TEXT)"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS app_state (
            id INTEGER PRIMARY KEY,
            app_version TEXT,
            are_users_informed INTEGER DEFAULT 0)"""
    )
    conn.commit()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            bill_label TEXT,
            payment_url TEXT,
            period INTEGER)"""
    )
    conn.commit()

    conn.close()


if __name__ == "__main__":
    initialize()
