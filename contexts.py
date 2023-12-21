from workout_utils import AvailableExercise
from telebot.types import Message
from user_body_profile_classes import UserBodyProfile

# class PayContext:
#     def __init__(self) -> None:
#         self.bill_label = None
#         self.period = None
# pay_contexts = {}

class UserContext:
    def __init__(self) -> None:
        self.username = None
user_contexts = {}

class WorkoutContext:
    def __init__(self) -> None:
        self.started_workout_id  = None
        self.selected_exercise:AvailableExercise = None
        self.started_exercise_table_id = None
        self.started_set_table_id = None
        self.last_equipment_weight = None
        self.finished_workouts = None
workout_contexts = {}

class FoodInputContext:
    def __init__(self) -> None:
        self.foods = []
        #self.nutritionix_cache_entry_id = None
    def clear(self) -> None:
        self.foods = None
        #self.data = None
food_input_contexts = {}

class BodyProfileFillingContext:
    def __init__(self) -> None:
        self.user_body_profile:UserBodyProfile = UserBodyProfile()
body_profile_filling_contexts = {}

class MealDiaryContext:
    def __init__(self) -> None:
        self.periods = {}
meal_diary_contexts = {}

class InputDietMacrosContext:
    def __init__(self) -> None:
        self.protein = None
        self.fat = None
        self.carbohydrate = None
        self.calories_range = None
input_diet_macros_contexts = {}

class InputBodyMeasurements:
    def __init__(self) -> None:
        self.measurements = {
            'shoulders': None,
            'forearms': None,
            'biceps': None,
            'chest': None,
            'waist': None,
            'thighs': None,
            'calves': None,
            'neck': None
            }
    def clear(self):
        self.measurements = {
            'shoulders': None,
            'forearms': None,
            'biceps': None,
            'chest': None,
            'waist': None,
            'thighs': None,
            'calves': None,
            'neck': None
            }
input_body_measurements_contexts = {}

class InputNewUserFoodsContext:
    def __init__(self) -> None:
        self.new_user_foods = []
input_new_user_foods_contexts = {}

class InputUserFoodToDiaryContext:
    def __init__(self) -> None:
        self.food = None
        self.calories_100g = None
        self.protein_100g = None
        self.fat_100g = None
        self.carbohydrate_100g = None

    def clear(self):
        self.food = None
        self.calories_100g = None
        self.protein_100g = None
        self.fat_100g = None
        self.carbohydrate_100g = None
input_user_food_to_diary_contexts = {}

class InputTimeZoneContext:
    def __init__(self) -> None:
        self.timezone = None
input_timezone_contexts = {}

# def get_pay_context(message:Message) -> PayContext:
#     chat_id = message.chat.id
#     if pay_contexts.get(chat_id) is None:
#         pay_contexts[chat_id] = PayContext()
#     return pay_contexts.get(chat_id)

def get_workout_context(message:Message) -> WorkoutContext:
    chat_id = message.chat.id
    if workout_contexts.get(chat_id) is None:
        workout_contexts[chat_id] = WorkoutContext()
    return workout_contexts.get(chat_id)

def clear_workout_context(message:Message) -> None:
    if chat_id := message.chat.id:
        workout_contexts[chat_id] = WorkoutContext()

def get_user_context(message:Message) -> UserContext:
    chat_id = message.chat.id
    if user_contexts.get(chat_id) is None:
        user_contexts[chat_id] = UserContext()
    return user_contexts.get(chat_id)

def get_body_profile_filling_context(message:Message) -> BodyProfileFillingContext:
    chat_id = message.chat.id
    if body_profile_filling_contexts.get(chat_id) is None:
        body_profile_filling_contexts[chat_id] = BodyProfileFillingContext()
    return body_profile_filling_contexts.get(chat_id)

def clear_body_profile_filling_context(message:Message):
    if chat_id := message.chat.id:
        body_profile_filling_contexts[chat_id] = BodyProfileFillingContext()

def get_food_input_context(message:Message) -> FoodInputContext:
    chat_id = message.chat.id
    if food_input_contexts.get(chat_id) is None:
        food_input_contexts[chat_id] = FoodInputContext()
    return food_input_contexts.get(chat_id)

def get_meal_diary_context(message:Message) -> MealDiaryContext:
    chat_id = message.chat.id
    if meal_diary_contexts.get(chat_id) is None:
        meal_diary_contexts[chat_id] = MealDiaryContext()
    return meal_diary_contexts.get(chat_id)

def get_input_diet_macros_context(message:Message) -> InputDietMacrosContext:
    chat_id = message.chat.id
    if input_diet_macros_contexts.get(chat_id) is None:
        input_diet_macros_contexts[chat_id] = InputDietMacrosContext()
    return input_diet_macros_contexts.get(chat_id)

def get_input_body_measurements_context(message:Message) -> InputBodyMeasurements:
    chat_id = message.chat.id
    if input_body_measurements_contexts.get(chat_id) is None:
        input_body_measurements_contexts[chat_id] = InputBodyMeasurements()
    return input_body_measurements_contexts.get(chat_id)

def get_input_new_user_foods_context(message:Message) -> InputNewUserFoodsContext:
    chat_id = message.chat.id
    if input_new_user_foods_contexts.get(chat_id) is None:
        input_new_user_foods_contexts[chat_id] = InputNewUserFoodsContext()
    return input_new_user_foods_contexts.get(chat_id)

def get_input_user_foods_to_diary_context(message:Message) -> InputUserFoodToDiaryContext:
    chat_id = message.chat.id
    if input_user_food_to_diary_contexts.get(chat_id) is None:
        input_user_food_to_diary_contexts[chat_id] = InputUserFoodToDiaryContext()
    return input_user_food_to_diary_contexts.get(chat_id)

def get_input_timezone_context(message:Message) -> InputTimeZoneContext:
    chat_id = message.chat.id
    if input_timezone_contexts.get(chat_id) is None:
        input_timezone_contexts[chat_id] = InputTimeZoneContext()
    return input_timezone_contexts.get(chat_id)

if __name__ == '__main__':
    pc = get_pay_context('Molot369')
    print(pc.period)