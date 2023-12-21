from googletrans import Translator

def translate_from_rus_to_eng(text):
    translator = Translator()
    translated = translator.translate(text, src='ru', dest='en')
    return translated.text

def translate_from_eng_to_rus(text):
    translator = Translator()
    translated = translator.translate(text, src='en', dest='ru')
    return translated.text

if __name__ == '__main__':
    print(translate_from_rus_to_eng('Яйца'))