from enum import Enum, unique

# @unique
# class Sex(Enum):
#     male = 0
#     female = 1

@unique
class PhysicalActivityLevel(Enum):
    SEDENTARY = 1.2
    LIGHTLY_ACTIVE = 1.375
    MODERATELY_ACTIVE = 1.55
    VERY_ACTIVE = 1.725
    EXTRA_ACTIVE = 1.9

# class Goal(Enum):
#     LOSS_WEIGHT = 0
#     BUILD_MUSCLE = 1
#     KEEP_WEIGHT = 2

class UserBodyProfileField(Enum):
    sex = 0
    birth_date = 1
    height = 2
    weight = 3
    physical_activity_level = 4
    goal = 5

class UserBodyProfile:
    def __init__(self, id=None, user_id=None, birth_date=None, height=None, weight=None, sex=None, physical_activity_level=None, BMI=None, BMR=None, TDEE=None, goal=None, body_fat_percentage=None):
        self.id = id
        self.user_id = user_id
        self.birth_date = birth_date
        self.height = height
        self.weight = weight
        self.sex = sex
        self.physical_activity_level = physical_activity_level
        self.BMI = BMI
        self.BMR = BMR
        self.TDEE = TDEE
        self.goal = goal


    # @property
    # def is_filled(self) -> bool:
    #     # Проверяем каждое поле на None
    #     fields = [
    #         self.birth_date, self.height, self.weight,
    #         self.sex, self.physical_activity_level,
    #         self.goal
    #     ]
    #     return all(field is not None and len(field) > 0 for field in fields)

if __name__ == '__main__':
    activity_level = getattr(PhysicalActivityLevel, 'SEDENTARY')
    print(activity_level.value)