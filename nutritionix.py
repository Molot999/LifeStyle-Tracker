import requests
from nutritionix_utils import NutritionixFood
from typing import List

# Замените значения NutritionixAppID и NutritionixAppKey на ваши собственные
nutritionix_app_id = "672c6c14"
nutritionix_app_key = "6f4ba779b23cefe6adf152de7860fc87"

# URL для запроса
natural_url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
search_url = "https://trackapi.nutritionix.com/v2/search/instant?query="

# Заголовки
headers = {
    "Content-Type": "application/json",
    "x-app-id": nutritionix_app_id,
    "x-app-key": nutritionix_app_key
}

def get_foods_list(query):
    # Тело запроса
    body = {
        "query": query,
        "timezone": "Europe/Moscow"
    }

    # Выполнение POST-запроса
    response = requests.post(natural_url, json=body, headers=headers)

    if response.status_code != 200:
        return None, None
    
    data = response.json()
    foods = data["foods"]
    return [NutritionixFood(food) for food in foods], str(data)

def search_upc_barcode(query):
    url = f'{search_url}{query}'
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None
    
    return response.json()
    # foods = data["foods"]
    # return [Food(food) for food in foods]

if __name__ == '__main__':
    fs = get_foods_list('1 boiled egg')