import requests

class NutritionixFood:
    def __init__(self, food:dict) -> None:
        self.food_name = food.get('food_name')
        self.brand_name = food.get('brand_name')
        self.serving_qty = food.get('serving_qty')
        self.serving_weight_grams = food.get('serving_weight_grams')
        self.nf_calories = food.get('nf_calories')
        self.nf_total_fat = food.get('nf_total_fat')
        self.nf_saturated_fat = food.get('nf_saturated_fat')
        self.nf_cholesterol = food.get('nf_cholesterol')
        self.nf_total_carbohydrate = food.get('nf_total_carbohydrate')
        self.nf_dietary_fiber = food.get('nf_dietary_fiber')
        self.nf_sugars = food.get('nf_sugars')
        self.nf_protein = food.get('nf_protein')
        self.nf_potassium = food.get('nf_potassium')
        self.nf_p = food.get('nf_p')
        self.full_nutrients = food.get('full_nutrients')
        self.photo_url = food.get('photo', {}).get('highres')
        self.barcode = food.get('upc')

query = '3 boiled eggs'

# Замените значения NutritionixAppID и NutritionixAppKey на ваши собственные
nutritionix_app_id = "000000"
nutritionix_app_key = "0000000000000000000000000000000"
nutritionix_app_id = "672c6c14"
nutritionix_app_key = "6f4ba779b23cefe6adf152de7860fc87"
# URL для запроса
natural_url = "https://trackapi.nutritionix.com/v2/natural/nutrients"

# Заголовки
headers = {
    "Content-Type": "application/json",
    "x-app-id": nutritionix_app_id,
    "x-app-key": nutritionix_app_key
}

# Тело запроса
body = {
    "query": query,
    "timezone": "US/Eastern"
}

# Выполнение POST-запроса
response = requests.post(natural_url, json=body, headers=headers)

if response.status_code == 200:
    data = response.json()
    foods = data["foods"]
    result = [NutritionixFood(food) for food in foods]

    #Тут делаем что-то с result, например:
    print(result[0].full_nutrients)