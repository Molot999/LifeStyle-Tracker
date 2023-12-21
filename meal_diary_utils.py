class UserMealDiaryProduct:
    def __init__(self, id, user_id, food_name, brand_name, serving_qty, serving_weight_grams, calories, total_fat, saturated_fat, cholesterol,
                total_carbohydrate, dietary_fiber, sugars, protein, potassium, p, full_nutrients, datetime):
        self.id = id
        self.user_id = user_id
        self.food_name = food_name
        self.brand_name = brand_name
        self.serving_qty = serving_qty
        self.serving_weight_grams = serving_weight_grams
        self.calories = calories
        self.total_fat = total_fat
        self.saturated_fat = saturated_fat
        self.cholesterol = cholesterol
        self.total_carbohydrate = total_carbohydrate
        self.dietary_fiber = dietary_fiber
        self.sugars = sugars
        self.protein = protein
        self.potassium = potassium
        self.p = p
        self.full_nutrients = full_nutrients
        self.datetime = datetime

def get_month_str(month_num):
    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
            'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    return months[int(month_num) - 1]