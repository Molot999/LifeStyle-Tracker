from typing import List

class ReceiptStep:
    def __init__(self, receipt_id=None, step_number=None, img_url=None, description=None) -> None:
        self.receipt_id = receipt_id
        self.number = step_number
        self.img_url = img_url
        self.description = description

class ReceiptIngredient:
    def __init__(self, id=None, receipt_id=None, title=None, weight=None) -> None:
        self.id = id
        self.receipt_id = receipt_id
        self.title = title
        self.weight = weight

class Receipt:
    def __init__(self, id=None, title=None, img_url=None, description=None, category_1=None, category_2=None, category_3=None,
                calories_100g=None, proteins_100g=None, fats_100g=None, carbohydrates_100g=None, url=None) -> None:
        self.id = id
        self.title = title
        self.img_url = img_url
        self.description = description
        self.category_1 = category_1
        self.category_2 = category_2
        self.category_3 = category_3
        self.calories_100g = calories_100g
        self.proteins_100g = proteins_100g
        self.fats_100g = fats_100g
        self.carbohydrates_100g = carbohydrates_100g
        self.url = url