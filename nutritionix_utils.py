import dbconnection as db
from typing import List

class NutritionixNutrient:
    def __init__(self, attr_id, usda_tag, name, unit, ru_name) -> None:
        self.attr_id = attr_id
        self.usda_tag = usda_tag
        self.name = name
        self.ru_name = ru_name
        self.unit = unit
        self.value = None

class NutritionixFood:
    def __init__(self, food:dict) -> None:
        self.food_name = food.get('food_name')
        self.brand_name = food.get('brand_name')
        self.serving_qty = food.get('serving_qty')
        self.serving_weight_grams = food.get('serving_weight_grams')
        self.nf_calories = food.get('nf_calories')
        #self.calories_100g = (self.nf_calories * 100) / self.serving_weight_grams
        self.nf_total_fat = food.get('nf_total_fat')
        self.nf_saturated_fat = food.get('nf_saturated_fat')
        self.nf_cholesterol = food.get('nf_cholesterol')
        self.nf_total_carbohydrate = food.get('nf_total_carbohydrate')
        self.nf_dietary_fiber = food.get('nf_dietary_fiber')
        self.nf_sugars = food.get('nf_sugars')
        self.nf_protein = food.get('nf_protein')
        self.nf_potassium = food.get('nf_potassium')
        self.nf_p = food.get('nf_p')
        self.full_nutrients:List[NutritionixNutrient] = [db.get_nutritionix_nutrient_info(nutrient_info.get('attr_id'), nutrient_info.get('value')) for nutrient_info in food.get('full_nutrients')]
        self.photo_url = food.get('photo', {}).get('thumb')
        self.barcode = food.get('upc')

if __name__ == '__main__':
    n1 = NutritionixNutrient(123, None, None, None, None)
    n1.value = 626
    n2 = NutritionixNutrient(681, None, None, None, None)
    n2.value = 474.2
    n3 = NutritionixNutrient(437, None, None, None, None)
    n3.value = 821
    n4 = NutritionixNutrient(161, None, None, None, None)
    n4.value = 12.5
    lst = [n1, n2, n3, n4]
    x = ''
    for n in lst:
        x += f',{n.attr_id}:{n.value}'
    print(x.strip(','))