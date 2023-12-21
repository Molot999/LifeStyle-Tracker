class UserDietMacros:
    def __init__(self, id, user_id, calories_range, protein_g, fat_g, carbohydrate_g) -> None:
            self.id = id
            self.user_id = user_id
            self.calories_range = calories_range
            self.protein_g = protein_g
            self.fat_g = fat_g
            self.carbohydrate_g = carbohydrate_g

NUTRIENT_CALORIES = {
    'protein':4,
    'fat':4,
    'carbohydrate':9
}

def calculate_protein_requirement(activity_level, goal):
    protein_requirements = {
    'LOSS_WEIGHT': {
        'SEDENTARY': 0.9,
        'LIGHTLY_ACTIVE': 1.1,
        'MODERATELY_ACTIVE': 1.3,
        'VERY_ACTIVE': 1.5,
        'EXTRA_ACTIVE': 1.7,
    },
    'KEEP_WEIGHT': {
        'SEDENTARY': 0.9,
        'LIGHTLY_ACTIVE': 1.1,
        'MODERATELY_ACTIVE': 1.3,
        'VERY_ACTIVE': 1.5,
        'EXTRA_ACTIVE': 1.7,
    },
    'BUILD_MUSCLE': {
        'SEDENTARY': 1.3,
        'LIGHTLY_ACTIVE': 1.5,
        'MODERATELY_ACTIVE': 1.7,
        'VERY_ACTIVE': 1.9,
        'EXTRA_ACTIVE': 2.1,
    },
    'MUSCLE_STRENGTH': {
        'SEDENTARY': 1.3,
        'LIGHTLY_ACTIVE': 1.5,
        'MODERATELY_ACTIVE': 1.7,
        'VERY_ACTIVE': 1.9,
        'EXTRA_ACTIVE': 2.1,
    },
}
    return protein_requirements[goal][activity_level]

def calculate_fat_requirement(activity_level):
    fat_requirements = {
        'SEDENTARY': 1,
        'LIGHTLY_ACTIVE': 1,
        'MODERATELY_ACTIVE': 1.1,
        'VERY_ACTIVE': 1.1,
        'EXTRA_ACTIVE': 1.2,
    }
    return fat_requirements[activity_level]

if __name__ == '__main__':
    weight = 106
    protein_requirement = calculate_protein_requirement('MODERATELY_ACTIVE', 'LOSS_WEIGHT')
    print('protein_requirement', protein_requirement * weight)
    fat_requirement = calculate_fat_requirement('MODERATELY_ACTIVE')
    print('fat_requirement', fat_requirement * weight)
    print('Ккал белки', protein_requirement * weight * NUTRIENT_CALORIES['protein'])
    print('Ккал жиры', fat_requirement * weight * NUTRIENT_CALORIES['fat'])