class UserFood:
    def __init__(self, id, user_id, barcode, title, group_name, weight, one_piece_weight,
                calories, fat, protein, carbohydrate, full_nutrients, is_animal_protein,
                is_unsaturated_fats, is_complex_carbohydrates):
        self.id = id
        self.user_id = user_id
        self.barcode = barcode
        self.title = title
        self.group_name = group_name
        self.weight = weight
        self.one_piece_weight = one_piece_weight
        self.calories = calories
        self.fat = fat
        self.protein = protein
        self.carbohydrate = carbohydrate
        self.full_nutrients = full_nutrients
        self.is_animal_protein = is_animal_protein
        self.is_unsaturated_fats = is_unsaturated_fats
        self.is_complex_carbohydrates = is_complex_carbohydrates

def parse_food_nutrients(food_nutrients):
    nutrients_data = str(food_nutrients).split(',') # Преобразуем входные данные в строку и разделяем по запятой
    nutrients_dict = {}  # Создаем пустой словарь для сохранения данных
    for nutrient in nutrients_data:
        title, value = nutrient.split(':') # Разделяем данные по двоеточию на название и значение
        nutrients_dict[title] = value if value != 'None' else None # Добавляем в словарь с соответствующими типами данных
    return nutrients_dict

def correct_user_foods_text_len(text, added_len):
    print(text)
    text_len_limit = 4000

    if len(text) + added_len <= text_len_limit:
        return text
    
    while len(text) + added_len > text_len_limit:
        text = text.split('\n')
        text = '\n'.join(text[:-1])
        if len(text) + added_len <= text_len_limit:
            return text