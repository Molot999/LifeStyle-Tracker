import dbinitializer
import dbconnection as db
from config import bot
import profile_manager
import keyboards
import subscriptions
import yoomoney_api
from contexts import *
import workouts
import exercises
import user_body_profiles
import nutritions
import meal_diaries
import meal_options
import user_diet_macros
import user_weight_diaries
import user_body_measurements
import workouts_statistics
from informer import isend
import receipts
import user_foods
import user_foods_editing
from notifications import send_notifications
import nutrient_report
import app_version_controller
from time import sleep
from subscriptions_utils import AvailableSubscription
import traceback

dbinitializer.initialize()
#app_version_controller.process_new_version_notifications_sending(disable_notification=False)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    start_param = message.text.split(' ')[1] if len(message.text.split(' ')) > 1 else None
    username = message.from_user.username
    user_context:UserContext = get_user_context(message)
    user_context.username = username
    bot.send_message(message.chat.id, 'Добро пожаловать в нашу группу - <b>@life_style_tracker</b>', parse_mode='HTML')
    bot.send_message(message.chat.id,
                    'Данный чат-бот находится на этапе бета-теста - в случае возникновения ошибки вызовите команду /start\nВсе вопросы и предложения можете направить в поддержку',
                    parse_mode='HTML')
    # Юзер уже зарегистрирован
    if db.check_user_exists(message.chat.id):
        user_status = 'Юзер зареган'
        name = db.get_name(message.chat.id)
        bot.send_message(message.chat.id, f'Привет, <b>{name}</b>! Рад снова тебя видеть', parse_mode='HTML', reply_markup=keyboards.main_keyboard())
        #profile_manager.process_location(message)
        subscriptions.check_subscription_status(message)
    # Юзер НЕ зарегистрирован
    else:
        # Получаем пригласительную ссылку
        user_status = 'Юзер НЕ зареган'
        bot.send_message(message.chat.id, 'Привет, давай знакомиться. Введи ниже свое имя')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(message, profile_manager.set_name)
    isend(text=f'{user_status} - источник: {start_param or ""}', username=user_context.username, chat_id=message.chat.id, func_name='start')

# Обработчик нажатия inline-кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_inline_button_click(call):
    # Получаем данные, связанные с нажатием кнопки
    data = call.data
    print('handle_inline_button_click', data)
    if '#' in str(call.data):
        data, value = str(call.data).split('#')
    message = call.message
    bot.clear_step_handler_by_chat_id(message.chat.id)

    #offer_subscription
    if data == 'input_promocode':
        #promocodes.offer_input_promocode(message)
        pass
    elif data == 'subscription':
        if value == 'test':
            subscriptions.apply_test_period(message)
        else:
            selected_subscription:AvailableSubscription = AvailableSubscription(*db.get_available_subscription(value))
            subscriptions.buy_subscription(message, selected_subscription.period, selected_subscription.price)

    #pay_keyboard
    elif data == 'check_payment':
        if value:
            if yoomoney_api.get_is_bill_paid(value):
                paid_status_message = 'Подписка успешно оплачена'
                if subscription_period := db.get_payment(value):
                    db.add_user_subscription(message.chat.id, period_days=subscription_period)
                else:
                    paid_status_message = 'Возникла ошибка. Попробуйте нажать снова или обратитесь в подержку'
            else:
                paid_status_message = 'Информации об оплате еще не поступило. Подождите пару минут или обратитесь в поддержку'

            bot.send_message(message.chat.id, paid_status_message)
        else:
            bot.send_message(message.chat.id, 'Возникла ошибка. Попробуйте нажать снова или обратитесь в подержку')

    #user_workouts
    elif data == 'new_workout':
        workouts.process_new_workout(message)
    elif data == 'continue_workout':
        is_workout_finished, started_workout_id = workouts.check_is_started_workout(message)
        if not is_workout_finished:
            workouts.continue_started_workout(message, started_workout_id)
        else:
            workouts.process_new_workout(message)
    elif data == 'workouts_stat':
        workouts_statistics.get_workouts_stat(message)

    #workout_keyboard
    elif data == 'new_exercise':
        workouts.process_exercise_searching(message)
    elif data == 'finish_workout':
        workouts.finish_workout(message)

    #selected_exercise_keyboard
    elif data == 'start_exercise':
        exercises.start_exercise(message)
    elif data == 'other_exercise':
        workouts.process_exercise_searching(message)

    #started_exercise_keyboard
    elif data == 'new_exercise_set':
        exercises.process_new_set_starting(message)
    elif data == 'finish_exercise':
        exercises.finish_exercise(message)

    #started_exercise_set_keyboard
    elif data == 'finish_exercise_set':
        exercises.process_exercise_set_finishing(message)
    elif data == 'undo_exercise_set':
        exercises.undo_exercise_set(message)

    #user_body_profile_filling_request
    elif data == 'yes_fill_body_profile':
        user_body_profiles.process_user_body_profile_filling(message)
    elif data == 'no_fill_body_profile':
        bot.send_message(message.chat.id, 'Окей, заполним позже')

    #nutritions_keyboard
    elif data == 'add_meal':
        nutritions.add_meal(message)
    elif data == 'user_foods':
        user_foods.process_user_foods(message)
    elif data == 'meal_diary':
        meal_diaries.process_meal_diary(message)
    elif data == 'receipts':
        receipts.process_receipts(message)
    elif data == 'meal_options':
        meal_options.process_meal_options(message)

    #handled_meal_keyboard
    elif data == 'true_handled_meal':
        nutritions.add_food_diary_entry(message)
    elif data == 'false_handled_meal':
        nutritions.add_meal(message)

    #diet_macros_keyboard
    elif data == 'true_diet_macros':
        user_diet_macros.save_user_diet_macros(message)
    elif data == 'false_diet_macros':
        user_id = db.get_user_id(message.chat.id)
        user_body_profile:UserBodyProfile = db.get_user_body_profile(user_id)
        user_diet_macros.process_input_diet_macros(message, user_body_profile)

    #user_body_profile_info_keyboard
    elif data == 'edit_body_profile':
        user_body_profiles.process_user_body_profile_filling(message, True)
    elif data == 'weight_diary':
        user_weight_diaries.print_user_weight_diary(message)
    elif data == 'add_weight_diary_entry':
        bot.clear_step_handler_by_chat_id(message.chat.id)
        user_weight_diaries.process_user_weight_diary_entry_adding(message)
    elif data == 'timezone':
        profile_manager.print_user_timezone(message)
    elif data == 'my_subscription':
        subscriptions.check_subscription_status(message)

    #meal_options_keyboard
    elif data == 'edit_meal_options':
        meal_options.edit_meal_options(message)

    #user_body_measurements_keyboard
    elif data == 'measurements_diary':
        user_body_measurements.print_user_body_measurements_diary(message)

    #user_meausurements_keyboard
    elif data == 'add_measurement':
        bot.clear_step_handler_by_chat_id(message.chat.id)
        user_body_measurements.process_body_measurements_adding(message)

    #workouts_statistics_keyboard
    elif data == 'general_stats':
        workouts_statistics.send_general_stats(message)
    elif data == 'exercise_stats':
        workouts_statistics.process_exercise_statistics(message)

    #receipts_keyboard
    elif data == 'random_receipt':
        receipts.process_random_receipt(message)
    elif data == 'search_receipt':
        receipts.process_receipt_searching(message)

    #random_receipt_keyboard
    elif data == 'another_random_receipt':
        receipts.process_random_receipt(message)

    #user_foods_keyboard
    elif data == 'search_user_foods':
        user_foods.search_user_food(message)
    elif data == 'edit_user_foods':
        user_foods_editing.process_user_foods_editing(message)

    #user_foods_editing_keyboard
    elif data == 'user_foods_upload':
        user_foods_editing.process_uploading_new_user_foods_table(message)
    elif data == 'user_foods_download':
        user_foods_editing.process_downloading_user_foods_table(message)
    elif data == 'user_foods_template':
        user_foods_editing.send_new_user_foods_table_template(message)
    elif data == 'process_deleting_user_foods':
        user_foods_editing.process_deleting_user_foods(message)

    #new_user_foods_table_info_keyboard
    elif data == 'confirm_new_user_foods':
        user_foods_editing.save_new_user_foods(message)
    elif data == 'decline_new_user_foods':
        user_foods_editing.process_uploading_new_user_foods_table(message)
    elif data == 'another_new_user_foods_example':
        user_foods_editing.send_new_user_foods_example(message)

    #user_food_info_keyboard
    elif data == 'add_user_food_to_meal_diary':
        user_foods.process_adding_user_food_to_meal_diary(message)

    #user_food_delete_checking_keyboard
    elif data == 'decline_new_user_foods':
        user_foods_editing.process_uploading_new_user_foods_table(message)
    elif data == 'another_new_user_foods_example':
        user_foods_editing.send_new_user_foods_example(message)

    #user_foods_delete_checking_keyboard
    elif data == 'delete_user_foods':
        user_foods_editing.delete_user_foods(message)
    elif data == 'cancel_deleting_user_foods':
        user_foods_editing.process_user_foods_editing(message)

    #meal_diary_keyboard
    elif data == 'nutrient_report':
        nutrient_report.process_nutrient_report_creating(message)

    #check_timezone_keyboard
    elif data == 'yes_timezone':
        profile_manager.save_timezone(message)
    elif data == 'no_timezone':
        profile_manager.send_processing_timezone_message(message)

    #delete_weight_diary_entry
    elif data == 'delete_weight_diary_entry':
        user_weight_diaries.delete_weight_diary_entry(message, value)

    #delete_body_measurements_entry_keyboard
    elif data == 'delete_body_measurements_entry':
        user_body_measurements.delete_body_measurements_entry(message, value)

    #delete_workout_keyboard
    elif data == 'delete_workout':
        workouts.delete_workout(message, value)

    #user_timezone_keyboard
    elif data == 'edit_timezone':
        profile_manager.send_processing_timezone_message(message)

    # Отправляем ответное сообщение для скрытия уведомления о нажатии кнопки
    bot.answer_callback_query(callback_query_id=call.id)

@bot.message_handler(commands=['clear_user_data'])
def clear_user_data(message:Message):
    user_id = db.get_user_id(message.chat.id)
    status = db.try_clear_user_data(message.chat.id, user_id)
    if status is True:
        bot.send_message(message.chat.id, 'Данные удалены')
    else:
        bot.send_message(message.chat.id, 'Произошла ошибка при удалении данных')

@bot.message_handler(commands=['clear_user_data_s'])
def clear_user_data(message:Message):
    status = db.try_clear_user_subscription(message.chat.id)
    if status is True:
        bot.send_message(message.chat.id, 'Данные о подписке удалены')
    else:
        bot.send_message(message.chat.id, 'Произошла ошибка при удалении данных подписки')

if __name__ == '__main__':
    import menu_buttons
    bot.register_message_handler(callback=menu_buttons.nutrition, func=lambda message: message.text == '🍽️Питание')
    bot.register_message_handler(callback=menu_buttons.workout, func=lambda message: message.text == '💪Тренировки')
    bot.register_message_handler(callback=menu_buttons.support, func=lambda message: message.text == '💬Поддержка')
    bot.register_message_handler(callback=menu_buttons.profile, func=lambda message: message.text == '👤Профиль')
    bot.register_message_handler(callback=menu_buttons.get_calculators, func=lambda message: message.text == '🔢Калькуляторы')
    #bot.register_message_handler(callback=barcode_reader.test, func=lambda message: message.text == 'test')

    while True:
        try:
            bot.polling(non_stop=True, interval=1, timeout=60)
        except Exception as _ex:
            print(_ex)
            traceback.print_exc()
            sleep(5)