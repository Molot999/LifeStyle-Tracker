from config import bot
from contexts import get_workout_context, WorkoutContext
import workouts
from workout_utils import Workout, AvailableExercise, WorkoutExercise, ExerciseSet
import keyboards
import dbconnection as db
import utils
from telebot.types import Message
import datetime
from informer import isend
import traceback
from user_body_profile_utils import is_valid_number

def get_exercise_sets_list(exercise_sets:list[ExerciseSet], is_strength_exercise:bool):
    exercise_sets_list = ''
    exercise_set_count = len(exercise_sets)
    for i, exercise_set in enumerate(exercise_sets):
        start_date = exercise_set.start_date
        start_date = utils.parse_date(start_date)
        if end_date := exercise_set.end_date:
            end_date = utils.parse_date(end_date)
            # Получение разницы во времени в секундах
            time_diff_seconds = int((end_date - start_date).total_seconds())
            mins, secs = divmod(time_diff_seconds, 60)
            duration_str = f"{str(mins).zfill(2) or 00}:{str(secs).zfill(2)}"
        else:
            duration_str = "?"

        if is_strength_exercise:
            exercise_sets_list += f'\n{i+1}) {exercise_set.rep_count}x{exercise_set.equipment_weight} ({duration_str})'
        else:
            exercise_sets_list += f'\n{i+1}) {duration_str}'


        exercise_set_end_date = exercise_set.end_date
        next_exercise_set = exercise_sets[i + 1] if i != exercise_set_count - 1 else None
        if exercise_set_end_date and next_exercise_set:
            exercise_set_end_date = utils.parse_date(exercise_set_end_date)
            next_exercise_set_start_date = utils.parse_date(next_exercise_set.start_date)
            # Получение разницы во времени в секундах
            time_diff_seconds = int((next_exercise_set_start_date - exercise_set_end_date).total_seconds())
            mins, secs = divmod(time_diff_seconds, 60)
            rest_duration_str = f"{str(mins).zfill(2)}:{str(secs).zfill(2)}"
            exercise_sets_list += f'\n<u>Отдых</u>: {rest_duration_str}'
        # previous_exercise_set: ExerciseSet = exercise_sets[i - 1] if i > 0 else None
        # next_exercise_set: ExerciseSet = exercise_sets[i + 1] if i < exercise_set_count - 1 else None
        # print(f'{i}/{exercise_set_count}')
        # print('previous_exercise_set', bool(previous_exercise_set))
        # print('next_exercise_set', bool(next_exercise_set))
        # if previous_exercise_set and next_exercise_set:
        #     previous_exercise_set_end_date = utils.parse_date(previous_exercise_set.end_date)
        #     next_exercise_set_start_date = utils.parse_date(next_exercise_set.start_date)
        #     # Получение разницы во времени в секундах
        #     time_diff_seconds = int((next_exercise_set_start_date - previous_exercise_set_end_date).total_seconds())
        #     mins, secs = divmod(time_diff_seconds, 60)
        #     rest_duration_str = f"{str(mins).zfill(2)}:{str(secs).zfill(2)}"
        #     exercise_sets_list += f'\n<u>Отдых</u>: {rest_duration_str}'

    return exercise_sets_list

def send_started_exercise_info(message:Message):
    isend(chat_id=message.chat.id, func_name='send_exercise_info')
    workout_context:WorkoutContext = get_workout_context(message)
    selected_exercise:AvailableExercise = workout_context.selected_exercise
    if not selected_exercise:
        bot.send_message(message.chat.id, 'Не удалось получить данные о тренировке, нажмите /start и продолжите')
        return
    started_exercise_table_id = workout_context.started_exercise_table_id
    exercise_sets:list[ExerciseSet] = db.get_exercise_sets(started_exercise_table_id)
    exercise_info = f'<b>{str(selected_exercise.title).capitalize()}</b>'
    if exercise_sets:
        is_strength_exercise = selected_exercise.ex_kind == 'Силовое'
        exercise_sets_list = get_exercise_sets_list(exercise_sets, is_strength_exercise)
    else:
        exercise_sets_list = '\nПодходов еще не было'

    exercise_info += exercise_sets_list

    bot.send_message(message.chat.id,
                    exercise_info,
                    'HTML',
                    reply_markup=keyboards.started_exercise_keyboard())

def start_exercise(message:Message):
    isend(chat_id=message.chat.id, func_name='start_exercise')
    workout_context = get_workout_context(message)
    started_workout_id = workout_context.started_workout_id
    if not started_workout_id:
        bot.send_message(message.chat.id, 'Не удалось получить данные о тренировке, нажмите /start и продолжите')
        return
    selected_exercise:AvailableExercise = workout_context.selected_exercise
    started_exercise_table_id = db.add_workout_exercise(started_workout_id, selected_exercise.id, utils.get_now_date())
    workout_context.started_exercise_table_id = started_exercise_table_id
    bot.send_message(message.chat.id,
                    f'Начинаем упражнение -> <b>{str(selected_exercise.title).capitalize()}</b>',
                    'HTML',
                    reply_markup=keyboards.started_exercise_keyboard())

def send_equipment_weight_message(message:Message):
    isend(chat_id=message.chat.id, func_name='send_equipment_weight_message')
    workout_context:WorkoutContext = get_workout_context(message)
    if workout_context.selected_exercise.ex_kind == 'Силовое':
        equipment_weight_message_text = 'Введите вес, который вы будете использовать в подходе (снаряда или утяжелителей):'
        if last_equipment_weight := workout_context.last_equipment_weight:
            equipment_weight_message_text = f'{equipment_weight_message_text[:-1]} или нажмите /last чтобы оставить прошлый (<b>{last_equipment_weight}</b>)'
        equipment_weight_message = bot.send_message(message.chat.id, equipment_weight_message_text, parse_mode='HTML')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(equipment_weight_message, equipment_weight_handler, last_equipment_weight)
    else:
        start_exercise_set(message, equipment_weight=None)

def send_equipment_weight_error_message(message:Message):
    isend(chat_id=message.chat.id, func_name='send_equipment_weight_error_message')
    equipment_weight_error_message = bot.send_message(message.chat.id, 'Ошибка! Вес может состоять из цифр, точки или запятой')
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(equipment_weight_error_message, equipment_weight_handler)

def equipment_weight_handler(message:Message, last_equipment_weight):
    isend(chat_id=message.chat.id, func_name='equipment_weight_handler', inputted_value=message.text)
    if equipment_weight := message.text:
        if equipment_weight == '/last' and last_equipment_weight:
            start_exercise_set(message, equipment_weight=last_equipment_weight)
        elif is_valid_number(equipment_weight):
            equipment_weight = float(equipment_weight)
            workout_context:WorkoutContext = get_workout_context(message)
            workout_context.last_equipment_weight = equipment_weight
            start_exercise_set(message, equipment_weight=equipment_weight)
        else:
            send_equipment_weight_error_message(message)
    else:
        send_equipment_weight_error_message(message)

def process_new_set_starting(message:Message):
    isend(chat_id=message.chat.id, func_name='process_new_set_starting')
    send_equipment_weight_message(message)

def start_exercise_set(message:Message, equipment_weight):
    isend(chat_id=message.chat.id, func_name='start_exercise_set')
    workout_context:WorkoutContext = get_workout_context(message)
    started_exercise_table_id = workout_context.started_exercise_table_id
    if not started_exercise_table_id:
            bot.send_message(message.chat.id, 'Не удалось получить данные о тренировке, нажмите /start и продолжите')
            return
    started_set_table_id = db.add_exercise_set(started_exercise_table_id, utils.get_now_date(), equipment_weight)
    workout_context.started_set_table_id = started_set_table_id
    bot.send_message(message.chat.id, 'Начинаем подход, когда закончите - нажмите кнопку ниже', reply_markup=keyboards.started_exercise_set_keyboard())

def process_exercise_set_finishing(message:Message):
    isend(chat_id=message.chat.id, func_name='process_exercise_set_finishing')
    workout_context:WorkoutContext = get_workout_context(message)
    if workout_context.selected_exercise.ex_kind == 'Силовое':
        send_rep_count_question_message(message)
    else:
        finish_exercise_set(message, rep_count=None)

def undo_exercise_set(message:Message):
    workout_context:WorkoutContext = get_workout_context(message)
    if started_set_table_id := workout_context.started_set_table_id:
        db.delete_exercise_set(started_set_table_id)
        workout_context.started_set_table_id = None
        workout_context.last_equipment_weight = None
    send_started_exercise_info(message)

def send_rep_count_question_message(message:Message):
    rep_count_question_message = bot.send_message(message.chat.id, 'Сколько повторений удалось сделать?')
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(rep_count_question_message, rep_count_handler)

def rep_count_handler(message:Message):
    rep_count = message.text
    if rep_count and is_valid_number(message.text):
        finish_exercise_set(message, rep_count=rep_count)
    else:
        equipment_weight_error_message = bot.send_message(message.chat.id, 'Ошибка! Введите число')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(equipment_weight_error_message, rep_count_handler)

def finish_exercise_set(message:Message, rep_count):
    bot.send_message(message.chat.id, '✅ Подход сохранен')
    workout_context:WorkoutContext = get_workout_context(message)
    started_set_table_id = workout_context.started_set_table_id
    if not started_set_table_id:
        bot.send_message(message.chat.id, 'Подход не найден')
        return
    db.update_exercise_set(started_set_table_id,
                            end_date=utils.get_now_date(),
                            rep_count=rep_count)
    send_started_exercise_info(message)

def finish_exercise(message:Message):
    isend(chat_id=message.chat.id, func_name='finish_exercise')
    workout_context:WorkoutContext = get_workout_context(message)
    workout_context.last_equipment_weight = None
    started_exercise_table_id = workout_context.started_exercise_table_id
    if not started_exercise_table_id:
        bot.send_message(message.chat.id, 'Не удалось получить данные о тренировке, нажмите /start и продолжите')
        return
    if db.get_exercise_sets(started_exercise_table_id):
        db.update_workout_exercise(started_exercise_table_id, end_date=utils.get_now_date())
    else:
        db.delete_workout_exercise(started_exercise_table_id)
    workout_context.started_exercise_table_id = None
    workouts.send_workout_exercises_data(message)