from config import bot
import keyboards
def nutrition(message):
    import nutritions
    nutritions.process_nutrition(message)

def workout(message):
    import workouts
    workouts.print_user_workouts(message)

def profile(message):
    import user_body_profiles
    user_body_profiles.check_user_body_profile_filling_status(message)

def support(message):
    bot.send_message(message.chat.id,
                    'Есть вопросы по работе приложения? Задай их, нажав на кнопку ниже',
                    reply_markup=keyboards.support_menu())
    
def get_calculators(message):
    import calculators
    calculators.send_calculators_message(message)