import sqlite3
import nltk
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
from config import bot
from collections import Counter
from pyaspeller import YandexSpeller
from workout_utils import AvailableExercise
from typing import List
import os

# Получение пути к текущей директории программы
current_directory = os.getcwd()

# Коэффициенты веса для метрик популярности
WEIGHT_DONE = 0.7
WEIGHT_VIEW = 0.3

speller = YandexSpeller()
# Инициализация NLP
#nltk.download('punkt', current_directory)
stemmer = SnowballStemmer('russian')

def process_exercise_searching(exercise_title) -> List[AvailableExercise]:
    # Фиксим правописание
    fixed_query = speller.spelled(exercise_title)
    if exercise_list := perform_search(fixed_query):
        return filter_titles_len(exercise_list)
    else:
        return None

def filter_titles_len(ex_list:List[AvailableExercise]):
    lengths = sum(len(str(s.title).replace(' ', '') + str(s.id)) + 1 for s in ex_list)
    print('Длина списка', lengths)
    while lengths > 30000:
        ex_list.pop()
        lengths = sum(len(s.title) for s in ex_list)
    return ex_list

def get_exercise_popularity(executions, views):
    return WEIGHT_DONE * executions + WEIGHT_VIEW * views

def jaccard_similarity(set1, set2):
    intersection_size = len(set1.intersection(set2))
    union_size = len(set1.union(set2))
    return intersection_size / union_size if union_size != 0 else 0

# Функция для приведения слова к его основе (стемминг)
def stem_word(word):
    x = stemmer.stem(word)
    print('stem_word', x)
    return x

# Функция для выполнения поиска с учетом различных форм слов
def perform_search(query) -> List[AvailableExercise]:
    conn = sqlite3.connect('lft.db')
    cursor = conn.cursor()

    # Токенизация запроса
    tokens = word_tokenize(query, language='russian')

    # Стемминг токенов
    stemmed_tokens = [stem_word(token) for token in tokens]

    # Формирование SQL-запроса с учетом разных форм слов
    search_query = "SELECT * FROM available_exercises WHERE "
    for idx, token in enumerate(stemmed_tokens):
        if idx > 0:
            search_query += " AND "
        search_query += f"title LIKE '%{token}%'"

    # Выполнение запроса к БД
    cursor.execute(search_query)
    results = cursor.fetchall()
    conn.close()
    if not results: return None
    # Вычисление коэффициента Жаккара для каждого упражнения и запроса
    search_results_with_similarity = []
    for result in results:
        available_exercise:AvailableExercise = AvailableExercise(*result)
        popularity = get_exercise_popularity(available_exercise.done_num, available_exercise.view_num)
        exercise_tokens = set(word_tokenize(available_exercise.title, language='russian'))
        similarity = jaccard_similarity(set(stemmed_tokens), exercise_tokens)
        available_exercise.popularity = popularity
        available_exercise.similarity = similarity
        search_results_with_similarity.append(available_exercise)

    search_results_with_similarity.sort(key=lambda ex: (ex.popularity, ex.similarity), reverse=True)

    return search_results_with_similarity

if __name__ == '__main__':
    print(stem_word('жим гантелей'))