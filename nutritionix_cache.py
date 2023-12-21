from typing import List
import mmh3
import dbconnection as db
from nutritionix_cache_utils import NutritionixCacheEntry
import datetime
from nutritionix_utils import NutritionixFood
import ast

def _create_murmurhash(input_string):
    return mmh3.hash(input_string)

def save_to_cache(query, data, entry_date):
    query_hash = _create_murmurhash(query)
    return db.add_nutritionix_cache_entry(query, query_hash, data, entry_date)

def search_query_response(query):
    try:
        query_hash = _create_murmurhash(query)
        if cache_entry_data := db.get_nutritionix_cache_entry_by_hash(query_hash):
            cache_found = True
            nutritionix_cache_entry:NutritionixCacheEntry = NutritionixCacheEntry(*cache_entry_data)
            if data := nutritionix_cache_entry.data:
                foods = parse_response(data)
            else:
                foods = None
        else:
            cache_found = False
            foods = None
    except Exception as e:
        print('Ошибка в search_query_response()', e)
        cache_found = None
        foods = None
    finally:
        return cache_found, foods

def sort_nutritionix_cache_entries(entries:List[NutritionixCacheEntry]):
    return sorted(entries, key=lambda x: (datetime.datetime.strptime(x.entry_date, "%d.%m.%Y %H:%M:%S")), reverse=True)

def parse_response(response_str):
    # Преобразование строки в словарь
    response_dict = ast.literal_eval(response_str)
    # Получение значения ключа "foods"
    foods_value = response_dict.get('foods')
    return tuple(NutritionixFood(food) for food in foods_value)

if __name__ == '__main__':
    query_data = search_query_response('4 вареных яйца')
    foods, data = query_data
    for f in foods:
        f:NutritionixFood = f
        print(f.food_name)