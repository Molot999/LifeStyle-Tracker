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
from receipts_utils import Receipt

# Получение пути к текущей директории программы
current_directory = os.getcwd()

speller = YandexSpeller()
# Инициализация NLP
#nltk.download('punkt', current_directory)
stemmer = SnowballStemmer('russian')

def process_receipt_searching(receipt_title) -> List[Receipt]:
    # Фиксим правописание
    fixed_query = speller.spelled(receipt_title)
    if receipt_list := perform_search(fixed_query):
        return filter_titles_len(receipt_list)[:15]
    else:
        return None

def filter_titles_len(receipts:List[Receipt]):
    def get_length():
        return sum(len(str(s.title) + str(s.id)) + 3 for s in receipts)
    
    lengths = get_length()
    while lengths > 30000:
        receipts.pop()
        lengths = get_length()
    return receipts

def jaccard_similarity(set1, set2):
    intersection_size = len(set1.intersection(set2))
    union_size = len(set1.union(set2))
    return intersection_size / union_size if union_size != 0 else 0

# Функция для приведения слова к его основе (стемминг)
def stem_word(word):
    x = stemmer.stem(word)
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
    search_query = "SELECT * FROM receipts WHERE "
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
        receipt:Receipt = Receipt(*result)
        exercise_tokens = set(word_tokenize(receipt.title, language='russian'))
        similarity = jaccard_similarity(set(stemmed_tokens), exercise_tokens)
        receipt.similarity = similarity
        search_results_with_similarity.append(receipt)

    search_results_with_similarity.sort(key=lambda ex: ex.similarity, reverse=True)

    return search_results_with_similarity

if __name__ == '__main__':
    pass