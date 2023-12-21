from telebot.types import Audio, Message, Voice
from config import bot
from utils import generate_random_filename
import os

def save_audiomessage(message):
    try:
        voice:Voice = message.voice
        file_info = bot.get_file(voice.file_id)
        filename = generate_random_filename(8)
        filepath = f'voices/{filename}.ogg'
        downloaded_file = bot.download_file(file_info.file_path)
        with open(filepath, "wb") as new_file:
            new_file.write(downloaded_file)
        return filepath
    except Exception as e:
        print('Ошибка в save_audiomessage()', e)
        return None

def delete_file(filepath):
    try:
        os.remove(filepath)
    except Exception as e:
        print('Ошибка в delete_file()', e)