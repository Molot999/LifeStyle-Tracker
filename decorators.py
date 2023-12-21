import menu_buttons

# Декоратор обработки ввода
def cancel_on_message_confusion(func):
    def wrapper(message, *args, **kwargs):
        if message.text is not None:
            handled_text = message.text
            if handled_text == '🍽️Питание':
                menu_buttons.nutrition(message)
                return
            elif handled_text == '💪Тренировки':
                menu_buttons.workout(message)
                return
            elif handled_text == '💬Поддержка':
                menu_buttons.support(message)
                return
            elif handled_text == '👤Профиль':
                menu_buttons.profile(message)
                return
            elif handled_text == '🔢Калькуляторы':
                menu_buttons.get_calculators(message)
                return
            elif handled_text == '/start':
                from main import start
                start(message)
                return
            elif handled_text in ['/exit', 'exit']:
                from config import bot
                bot.send_message(message.chat.id, 'Окэй, продолжим...')
                return
        return func(message, *args, **kwargs)
    return wrapper