from config import bot
from contexts import get_user_context, get_workout_context, clear_workout_context, UserContext, WorkoutContext
import dbconnection as db
import keyboards
import utils
from workout_utils import AvailableExercise, ExerciseSet, WorkoutExercise, Workout
import datetime
import workouts_analyzer
from telebot import types
import exercise_searcher
from typing import List
from decorators import cancel_on_message_confusion
import traceback
from exercises import send_started_exercise_info
from user_timezone import convert_to_user_local_time
from subscriptions_manager import check_subscription

def print_user_workouts(message, add_text=True):  # sourcery skip: move-assign
    if user_workouts := db.get_user_workouts(message.chat.id):
        if finished_workouts := [user_workout for user_workout in user_workouts if user_workout.end_date]:
            workout_context:WorkoutContext = get_workout_context(message)
            workout_context.finished_workouts = finished_workouts
            user_has_workouts = True
            user_id = db.get_user_id(message.chat.id)
            user_timezone = db.get_user_timezone(user_id) or '+05:00'
            msg_text = 'Здесь список ваших завершенных тренировок, нажмите на соответствующую команду слева от нее, чтобы просмотреть подробные данные:\n' if add_text else ''
            for num, workout in enumerate(finished_workouts, 1):
                workout.number = num
                if start_date := workout.start_date:
                    start_date_datetime = utils.parse_date(start_date)
                    start_date_str = utils.format_date(start_date_datetime)
                    start_date_str = convert_to_user_local_time(start_date_str, user_timezone, '%d.%m.%Y %H:%M')
                    duration = ''
                    if end_date := workout.end_date:
                        end_date_datetime = utils.parse_date(end_date)
                        duration = f' ({utils.get_minutes_diff(start_date_datetime, end_date_datetime)} мин.)\n'
                    msg_text += f"/{num} {start_date_str}{duration}"
        else:
            user_has_workouts = False
            msg_text = 'У вас нет законченных тренировок'
    else:
        user_has_workouts = False
        msg_text = 'Вы еще не проводили тренировок'

    is_workout_finished, _ = check_is_started_workout(message)
    msg = bot.send_message(message.chat.id, msg_text, reply_markup=keyboards.user_workouts(is_workout_finished == False))
    if user_has_workouts:
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(msg, workout_num_handler, finished_workouts)

@cancel_on_message_confusion
def workout_num_handler(message, finished_workouts:List[Workout]):
    workout_context:WorkoutContext = get_workout_context(message)
    finished_workouts:List[Workout] = workout_context.finished_workouts
    if not finished_workouts:
        bot.send_message(message.chat.id, 'Не удалось получить данные о тренировках, нажмите /start и продолжите')
        return
    workout_num = str(message.text).replace('/', '')
    if workout_num.isdigit() and int(workout_num) in [workout.number for workout in finished_workouts]:
        if selected_workout_list := [
            workout
            for workout in finished_workouts
            if workout.number == int(workout_num)
        ]:
            send_workout_info(message, selected_workout_list[0].id, is_selecting=True)
        else:
            bot.send_message(message.chat.id, 'Ошибка. Тренировка не найдена')
    else:
        bot.send_message(message.chat.id, 'Нажмите на команду с ID тренировки, чтобы просмотреть подробную сводку')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(message, workout_num_handler)

def check_is_started_workout(message) -> bool:
    if user_workouts := db.get_user_workouts(message.chat.id):
        last_workout = user_workouts[-1]
        is_workout_finished = last_workout.end_date is not None
        last_workout_id = last_workout.id
    else:
        is_workout_finished = True
        last_workout_id = None
    
    return is_workout_finished, last_workout_id
    
def check_is_started_workout_exercise(workout_id) -> bool:
    if workout_exercises := db.get_workout_exercises(workout_id):
        last_workout_exercise = workout_exercises[-1]
        is_exercise_finished = last_workout_exercise.end_date is not None
        exercise_table_id = last_workout_exercise.id
        exercise_id = last_workout_exercise.exercise_id
    else:
        is_exercise_finished = True
        exercise_table_id = None
        exercise_id = None

    return is_exercise_finished, exercise_table_id, exercise_id

def check_is_started_exercise_set(exercise_table_id):
    if exercise_sets := db.get_exercise_sets(exercise_table_id):
        last_exercise_set = exercise_sets[-1]
        is_exercise_set_finished = last_exercise_set.end_date is not None
        exercise_set_id = last_exercise_set.id
        equipment_weight = last_exercise_set.equipment_weight
    else:
        is_exercise_set_finished = True
        exercise_set_id = None
        equipment_weight = None
    return is_exercise_set_finished, exercise_set_id, equipment_weight

def continue_started_workout(message, started_workout_id):
    workout_context:WorkoutContext = get_workout_context(message)
    workout_context.started_workout_id = started_workout_id
    is_exercise_finished, exercise_table_id, exercise_id = check_is_started_workout_exercise(started_workout_id)
    if not is_exercise_finished:
        workout_context.started_exercise_table_id = exercise_table_id
        selected_exercise:AvailableExercise = db.get_available_exercise(exercise_id)
        workout_context.selected_exercise = selected_exercise
        is_exercise_set_finished, exercise_set_id, equipment_weight = check_is_started_exercise_set(exercise_table_id)
        if not is_exercise_set_finished:
            workout_context.started_set_table_id = exercise_set_id
            workout_context.last_equipment_weight = equipment_weight
            if selected_exercise.ex_kind == 'Силовое':
                started_set_info = f'Начат подход с весом <b>{equipment_weight}</b> кг в упражнении <b>{str(selected_exercise.title).capitalize()}</b>'
            else:
                started_set_info = f'Начат подход в упражнении <b>{str(selected_exercise.title).capitalize()}</b>'
            bot.send_message(message.chat.id,
                            started_set_info,
                            reply_markup=keyboards.started_exercise_set_keyboard(),
                            parse_mode='HTML')
        else:
            send_started_exercise_info(message)
    else:
        send_workout_exercises_data(message)

@check_subscription
def process_new_workout(message):
    is_workout_finished, started_workout_id = check_is_started_workout(message)
    if not is_workout_finished:
        continue_started_workout(message, started_workout_id)
    else:
        started_workout_id = db.add_user_workout(message.chat.id, utils.get_now_date())
        workout_context = get_workout_context(message)
        workout_context.started_workout_id = started_workout_id
        bot.send_message(message.chat.id, 'Начинаем новую тренировку', reply_markup=keyboards.workout_keyboard())

def process_exercise_searching(message):
    bot.send_message(message.chat.id, 'Введите название упражнения:', reply_markup=keyboards.exercise_searching_keyboard())
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(message, exercise_title_handler)

@cancel_on_message_confusion
def exercise_title_handler(message):
    if exercise_title := message.text:
        exercise_list_message, available_exercises = process_exercise_title_searching(exercise_title)
        if exercise_list_message and available_exercises:
            if len(available_exercises) > 1:
                msg = bot.send_message(message.chat.id, exercise_list_message, 'HTML', reply_markup=keyboards.exercise_list_keyboard())
                bot.clear_step_handler_by_chat_id(message.chat.id)
                bot.register_next_step_handler(msg, available_exercise_id_handler, available_exercises)
            else:
                exercise_id = available_exercises[0].id
                send_selected_exercise_message(message, int(exercise_id), available_exercises)
            return
        else:
            msg = bot.send_message(message.chat.id, 'Подходящих упражнений не найдено. Попробуйте еще раз:')
    else:
        msg = bot.send_message(message.chat.id, 'Введите название упражнения для поиска:')

    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(msg, exercise_title_handler)

def process_exercise_title_searching(exercise_title):
    if available_exercises := exercise_searcher.process_exercise_searching(exercise_title):
        exercise_list_message = 'Выберите соответствующее упражнение, нажав на команду слева:'
        for exercise in available_exercises:
            exercise_list_message += f'\n/{exercise.id} <b>{str(exercise.title).capitalize()}</b>'
    else:
        exercise_list_message = None
    return exercise_list_message, available_exercises

@cancel_on_message_confusion
def available_exercise_id_handler(message, available_exercises:List[AvailableExercise]):
    bot.clear_step_handler_by_chat_id(message.chat.id)
    if exercise_id_command := message.text:
        exercise_id = str(exercise_id_command).replace('/', '')
        if exercise_id.isdigit() and int(exercise_id) in [exercise.id for exercise in available_exercises]:
            send_selected_exercise_message(message, int(exercise_id), available_exercises)
            return
        else:
            msg = bot.send_message(message.chat.id, 'Ошибка. Введена неверная команда')
    else:
        msg = bot.send_message(message.chat.id, 'Ошибка. Выберите соответствующее упражнение нажав на команду слева от его названия')

    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(msg, available_exercise_id_handler, available_exercises)

def send_selected_exercise_message(message, exercise_id, available_exercises:List[AvailableExercise]):
    if exercise := get_selected_exercise(exercise_id, available_exercises):
        send_exercise_photos(message, exercise_id)
        send_exercise_info(message, exercise)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Данные упражнения не найдены. Попробуйте выбрать другое упражнение:')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(message, available_exercise_id_handler, available_exercises)

def get_selected_exercise(exercise_id, available_exercises:List[AvailableExercise]):
    # sourcery skip: use-next
    # Итерируемся по списку объектов и ищем значение атрибута `id`
    for exercise in available_exercises:
        if exercise.id == exercise_id:
            return exercise
    return None

def send_exercise_photos(message, exercise_id):
    user_id = db.get_user_id(message.chat.id)
    user_body_profile = db.get_user_body_profile(user_id)
    user_sex = user_body_profile.sex if user_body_profile else 'male'
    if exercise_photo_urls := db.get_available_exercise_photo_urls(exercise_id, user_sex):
        media = [
            types.InputMediaPhoto(photo_path, str(num))
            for num, photo_path in enumerate(exercise_photo_urls, 1)
        ]
        bot.send_media_group(message.chat.id, media)
    else:
        print('Фото для упражнения нет')

def send_exercise_info(message, exercise):
    workout_context = get_workout_context(message)
    workout_context.selected_exercise = exercise
    exercise_info_message = f'''
<b>{str(exercise.title).capitalize()}</b>
<b>Сложность:</b> {exercise.difficulty_level or 'нет'}
<b>Группа мышц:</b> {exercise.muscle_group or 'нет'}
<b>Дополнительные мышцы:</b> {exercise.additional_muscles or 'нет'}
<b>Тип:</b> {exercise.ex_type or 'нет'}
<b>Вид:</b> {exercise.ex_kind or 'нет'}
<b>Оборудование:</b> {exercise.equipment or 'нет'}
'''
    bot.send_message(message.chat.id, exercise_info_message, 'HTML', reply_markup=keyboards.selected_exercise_keyboard())

def send_workout_exercises_data(message):
    workout_context:WorkoutContext = get_workout_context(message)
    started_workout_id = workout_context.started_workout_id
    if not started_workout_id:
        bot.send_message(message.chat.id, 'Не удалось получить данные о тренировке, нажмите /start и продолжите')
        return
    if workout_exercises := db.get_workout_exercises(started_workout_id):
        workout_data_msg = ''
        for i, workout_exercise in enumerate(workout_exercises, 1):
            exercise_id = workout_exercise.exercise_id
            exercise:AvailableExercise = db.get_available_exercise(exercise_id)
            exercise_sets:List[ExerciseSet] = db.get_exercise_sets(workout_exercise.id) or []
            if exercise_sets:
                if exercise.ex_kind == 'Силовое':
                    exercise_sets_info_list = [f'{exercise_set.rep_count}x{exercise_set.equipment_weight}' for exercise_set in exercise_sets]
                else:
                    exercise_sets_info_list = []
                    for exercise_set in exercise_sets:
                        if end_date := exercise_set.end_date:
                            end_date = utils.parse_date(end_date)
                            start_date = utils.parse_date(exercise_set.start_date)
                            time_diff_seconds = int((end_date - start_date).total_seconds())
                            mins, secs = divmod(time_diff_seconds, 60)
                            set_duration_str = f"{str(mins).zfill(2) or 00}:{str(secs).zfill(2)}"
                            exercise_sets_info_list.append(set_duration_str)
                        else:
                            db.delete_exercise_set(exercise_set.id)
                            continue

                total_sets_time_seconds = 0
                for exercise_set in exercise_sets:
                    if end_date := exercise_set.end_date:
                        end_date = utils.parse_date(end_date)
                        start_date = utils.parse_date(exercise_set.start_date)
                        time_diff_seconds = int((end_date - start_date).total_seconds())
                        total_sets_time_seconds += time_diff_seconds
                mins, secs = divmod(total_sets_time_seconds, 60)
                total_sets_duration = f"{str(mins).zfill(2) or 00}:{str(secs).zfill(2)}"

                workout_data_msg += f'''
{i}) <b>{str(exercise.title).capitalize()}</b>
Подходов: {len(exercise_sets)} - {", ".join(exercise_sets_info_list)}
Время выполнения: {total_sets_duration}'''
                
            else:
                db.delete_workout_exercise(workout_exercise.id)
                workout_data_msg = 'Упражнения в данной тренировке пока что отсутствуют'
    else:
        workout_data_msg = 'Упражнения в данной тренировке пока что отсутствуют'
    bot.send_message(message.chat.id, workout_data_msg, 'HTML', reply_markup=keyboards.workout_keyboard())

def finish_workout(message):
    workout_context:WorkoutContext = get_workout_context(message)
    started_workout_id = workout_context.started_workout_id
    if not started_workout_id:
        bot.send_message(message.chat.id, 'Не удалось получить данные о тренировке, нажмите /start и продолжите')
        return
    if db.get_workout_exercises(started_workout_id):
        db.update_user_workout(started_workout_id, end_date=utils.get_now_date())
        bot.send_message(message.chat.id, '✔️Тренировка окончена')
        send_workout_info(message, started_workout_id)
    else:
        db.delete_user_workout(started_workout_id)
        bot.send_message(message.chat.id, '❎Тренировка удалена')
    clear_workout_context(message)

def send_workout_info(message, workout_id, is_selecting=False):
    try:
        workout = db.get_user_workout(workout_id)
        workout_start_date = utils.parse_date(workout.start_date)
        workout_end_date = utils.parse_date(workout.end_date)
        time_diff_seconds = int((workout_end_date - workout_start_date).total_seconds())
        workout_duration_mins = time_diff_seconds // 60
        workout_exercises = db.get_workout_exercises(workout_id)
        workout_info_msg = f'<b>Длительность:</b> {workout_duration_mins} мин'
        workout_volume = 0
        workout_rep_count = 0
        for exercise in workout_exercises:
            exercise_table_id = exercise.id
            if exercise_sets := db.get_exercise_sets(exercise_table_id):
                for exercise_set in exercise_sets:
                        if exercise_set:
                            rep_count = exercise_set.rep_count or 0
                            equipment_weight = exercise_set.equipment_weight or 0
                            workout_rep_count += rep_count
                            exercise_set_volume = rep_count*equipment_weight
                            workout_volume += exercise_set_volume
        if workout_rep_count != 0:
            workout_intensity = round(workout_volume / workout_rep_count, 2)
        else:
            workout_intensity = 0
        workout_info_msg += f'\n<b>Объем (тоннаж):</b> {workout_volume} кг'
        workout_info_msg += f'\n<b>Интенсивность (средний вес):</b> {workout_intensity} кг'
        workout_info_msg += f'\n<b>Упражнений:</b> {len(workout_exercises)}'
        #workout_info_msg += f'\n\nЧтобы просмотреть другую тренировку - нажмите на соответствующую команду'
        db.update_user_workout(workout_id, volume=workout_volume, intensity=workout_intensity, duration_mins=workout_duration_mins)
        if is_selecting:
            workout_info_msg += '\n\nМожете выбрать другую тренировку, нажав на ее команду'

        msg = bot.send_message(message.chat.id, workout_info_msg, parse_mode='HTML', reply_markup=keyboards.delete_workout_keyboard(workout.id))
        if is_selecting:
            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(msg, workout_num_handler)

    except Exception as e:
        print('Ошибка в send_workout_info()', e)
        traceback.print_exc()

    finally:
        print_user_workouts(message, add_text=False)

def delete_workout(message, workout_id):
    db.delete_user_workout(workout_id)
    bot.send_message(message.chat.id, '❎Тренировка удалена')
    print_user_workouts(message)