import requests
from yandex_cloud_config import STT_URL, API_KEY_HEADER

def get_text_from_speech(file_path):
    try:
        # Открываем и читаем аудиофайл в бинарном режиме
        with open(file_path, 'rb') as audio_file:
            audio_data = audio_file.read()

        # Отправляем POST-запрос на сервер Яндекс Speech Kit
        response = requests.post(STT_URL, headers=API_KEY_HEADER, data=audio_data)

        # Получаем результаты распознавания
        if response.ok:
            result = response.json()
            return result.get('result')
        else:
            return None
    except Exception as e:
        print('Ошибка в get_text_from_speech() - ', e)
        return None