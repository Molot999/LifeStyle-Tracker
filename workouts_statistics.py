from config import bot
from contexts import get_user_context, get_workout_context, clear_workout_context, UserContext, WorkoutContext
import dbconnection as db
import keyboards
import utils
from workout_utils import AvailableExercise, ExerciseSet, WorkoutExercise, Workout
import datetime
import workouts_analyzer
from telebot.types import Message, InputMediaPhoto
from typing import List, Dict, Tuple
from workout_utils import Workout, WorkoutExercise, ExerciseSet
from calculator_formulas import onerm_langer_formula, onerm_mayhew_watanabe_formula, onerm_repsch_formula
import numpy as np
from decorators import cancel_on_message_confusion
from subscriptions_manager import check_subscription

@check_subscription
def get_workouts_stat(message:Message):
    if user_workouts := db.get_user_workouts(message.chat.id):
        if len(user_workouts) >= 3:
            bot.send_message(message.chat.id,
'''Здесь вы можете просмотреть статистику по проведенным тренировкам:
<b>Общая статистика</b> содержит графики по всем тренировкам: продолжительность, тоннаж и интенсивность (средний вес)
<b>Статистика по упражнениям</b> содержит сводку по каждому упражнению, которое вы провели - максимальный вес, средний вес и др.''', parse_mode='HTML', reply_markup=keyboards.workouts_statistics_keyboard())
        else:
            workouts_left = 3 - len(user_workouts)
            bot.send_message(message.chat.id, f'Для формирования статистики осталось провести тренировок: <b>{workouts_left}</b>', parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, 'Вы еще не проводили тренировок')
    
def send_general_stats(message:Message):
    user_workouts = db.get_user_workouts(message.chat.id)
    for w in user_workouts:
        print(w.id)
    user_id = db.get_user_id(message.chat.id)
    volume_list = [workout.volume for workout in user_workouts]
    print(volume_list)
    intensity_list = [workout.intensity for workout in user_workouts]
    print(intensity_list)
    time_list = [workout.duration_mins for workout in user_workouts]
    print(time_list)
    workouts_analyzer.get_graph(user_id, len(user_workouts), workouts_analyzer.Graph_Type.volume, volume_list)
    workouts_analyzer.get_graph(user_id, len(user_workouts), workouts_analyzer.Graph_Type.intensity, intensity_list)
    workouts_analyzer.get_graph(user_id, len(user_workouts), workouts_analyzer.Graph_Type.duration, time_list)
    # Создаем объекты InputMediaPhoto для каждой картинки
    photo1 = InputMediaPhoto(open(f'workout_stats/{user_id}_volume.jpg', 'rb'))
    photo2 = InputMediaPhoto(open(f'workout_stats/{user_id}_intensity.jpg', 'rb'))
    photo3 = InputMediaPhoto(open(f'workout_stats/{user_id}_duration.jpg', 'rb'))
    #Отправляем группу картинок
    bot.send_media_group(message.chat.id, [photo1, photo2, photo3])

def get_exercise_statistics(message:Message) -> Dict[int, List[ExerciseSet]]:
    user_workouts:List[Workout] = db.get_user_workouts(message.chat.id)
    user_exercises:List[WorkoutExercise] = []
    for user_workout in user_workouts:
        user_exercises += db.get_workout_exercises(user_workout.id)
    exercise_sets_dict = {}
    for user_exercise in user_exercises:
        available_exercise_id = user_exercise.exercise_id
        exercise_id = user_exercise.id
        exercise_sets = db.get_exercise_sets(exercise_id)
        exercise_sets_dict.setdefault(available_exercise_id, []).extend(exercise_sets or [])
    return exercise_sets_dict

def process_exercise_statistics(message:Message):
    exercise_statistics:Dict[int, List[ExerciseSet]] = get_exercise_statistics(message)
    if len(exercise_statistics) == 1:
        exercise_statistics_msg = ''
        for available_exercise_id, exercise_set_list in exercise_statistics.items():
            exercise_statistics_msg += get_exercise_analyzing_str(available_exercise_id, exercise_set_list)
        bot.send_message(message.chat.id, exercise_statistics_msg, parse_mode='HTML')
    else:
        sorted_exercise_statistics = sorted(exercise_statistics.items(), key=lambda item: len(item[1]), reverse=True)
        send_exercise_list(message, sorted_exercise_statistics)

def get_exercise_analyzing_str(available_exercise_id, exercise_set_list:List[ExerciseSet]):
    available_exercise:AvailableExercise = db.get_available_exercise(available_exercise_id)
    exercise_title = str(available_exercise.title).capitalize()
    exercise_weights = [float(exercise_set.equipment_weight) for exercise_set in exercise_set_list if exercise_set.equipment_weight]
    exercise_set_tonnages = [
        float(exercise_set.rep_count) * float(exercise_set.equipment_weight)
        if exercise_set.rep_count is not None and exercise_set.equipment_weight is not None
        else 0
        for exercise_set in exercise_set_list
    ]
    exercise_max_set_tonnage = np.max(exercise_set_tonnages) if exercise_set_tonnages else '?'
    exercise_durations = [
        (utils.parse_date(exercise_set.end_date) - utils.parse_date(exercise_set.start_date)).total_seconds()
        if exercise_set.end_date is not None and exercise_set.start_date is not None
        else 0
        for exercise_set in exercise_set_list
    ]
    exercise_total_duration = sum(exercise_durations)

    exercise_weight_reps = [
        (float(exercise_set.equipment_weight), int(exercise_set.rep_count))
        if exercise_set.equipment_weight is not None and exercise_set.rep_count is not None
        else (0.0, 0)
        for exercise_set in exercise_set_list
    ]
    exercise_1rms_langer = [
        onerm_langer_formula(exercise_weight_rep[0], exercise_weight_rep[1])
        for exercise_weight_rep in exercise_weight_reps
    ]
    exercise_1rms_mayhew_watanabe = [
        onerm_mayhew_watanabe_formula(exercise_weight_rep[0], exercise_weight_rep[1])
        for exercise_weight_rep in exercise_weight_reps
    ]
    exercise_1rms_repsch = [
        onerm_repsch_formula(exercise_weight_rep[0], exercise_weight_rep[1])
        for exercise_weight_rep in exercise_weight_reps
    ]
    exercise_max_1rms = [
    np.max(exercise_1rms_langer) if exercise_1rms_langer else 0,
    np.max(exercise_1rms_mayhew_watanabe) if exercise_1rms_mayhew_watanabe else 0,
    np.max(exercise_1rms_repsch) if exercise_1rms_repsch else 0
    ]
    analyzing_text =  f'''
<b>{exercise_title}</b>
🏋️ <u>Вес</u>
Максимальный: {round(np.max(exercise_weights), 2) if exercise_weights else '?'} кг
Максимальный объем за подход: {exercise_max_set_tonnage} кг
Средний: {round(np.mean(exercise_weights), 2) if exercise_weights else '?'} кг
Медиана: {round(np.median(exercise_weights), 2) if exercise_weights else '?'} кг
Стандартное отклонение: {round(np.std(exercise_weights), 2) if exercise_weights else '?'} кг
🕒 <u>Длительность</u>
Общая: {round(exercise_total_duration/60) if exercise_total_duration else '?'} мин
Максимальная: {round(np.max(exercise_durations)) if exercise_durations else '?'} сек
Средняя: {round(np.mean(exercise_durations)) if exercise_durations else '?'} сек
Медиана: {round(np.median(exercise_durations), 2) if exercise_durations else '?'} сек
Стандартное отклонение: {round(np.std(exercise_durations), 2) if exercise_durations else '?'} сек
📊 <u>Проноз</u>
Максимальный вес (1RM): {round(np.mean(exercise_max_1rms)) if any(value != 0 for value in exercise_max_1rms) else '?'} кг
'''
    return analyzing_text

def send_exercise_list(message:Message, sorted_exercise_statistics:Tuple):
    exercises_list_msg = ''
    for exercise_stats in sorted_exercise_statistics:
        available_exercise_id = exercise_stats[0]
        available_exercise = db.get_available_exercise(available_exercise_id)
        exercises_list_msg += f'/{available_exercise_id} {str(available_exercise.title).capitalize()}\n'
    bot.send_message(message.chat.id, exercises_list_msg)
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(message, exercise_id_handler, sorted_exercise_statistics)

@cancel_on_message_confusion
def exercise_id_handler(message:Message, sorted_exercise_statistics:Tuple):
    if exercise_id_command := message.text:
        exercise_id_str = exercise_id_command.replace('/', '')
        if exercise_id_str.isdigit() and int(exercise_id_str) in [exercise_stats[0] for exercise_stats in sorted_exercise_statistics]:
            available_exercise_id = int(exercise_id_str)
            if selected_exercise_sets_list := [exercise_stats for exercise_stats in sorted_exercise_statistics if exercise_stats[0] == available_exercise_id]:
                selected_exercise_sets_list = selected_exercise_sets_list[0]
                bot.send_message(
                    message.chat.id,
                    f'{get_exercise_analyzing_str(available_exercise_id, selected_exercise_sets_list[1])}\nЧтобы просмотреть другое упражнение - нажмите на команду слева',
                    parse_mode='HTML',
                )
            else:
                bot.send_message(message.chat.id, 'Возникла ошибка. Попробуйте еще раз:')
        else:
            bot.send_message(message.chat.id, 'Неверная команда. Попробуйте еще раз:')
    else:
        bot.send_message(message.chat.id, 'Ошибка. Нажмите на команду:')

    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(message, exercise_id_handler, sorted_exercise_statistics)

if __name__ == '__main__':
    get_exercise_statistics()