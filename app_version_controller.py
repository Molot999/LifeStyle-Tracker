import dbconnection as db
from notifications import send_notifications
from config import APP_VERSION, IS_TEST
import threading

class AppState:
    def __init__(self, id, app_version, are_users_informed) -> None:
        self.id = id,
        self.app_version = app_version,
        self.are_users_informed = are_users_informed

def process_new_version_notifications_sending(disable_notification=True):
    if not IS_TEST:
        print('Бот в режиме релиза, запуск уведомлений')
        app_state:AppState = _get_app_state_info(APP_VERSION)
        if app_state and not app_state.are_users_informed:
            notification_start = '''
🚀 Йоу! Бот обновлен. Нажми /start чтобы продолжить'''
            threading.Thread(target=send_notifications, args=(notification_start, disable_notification)).start()
            db.update_app_state_info(APP_VERSION, True)

def _get_app_state_info(APP_VERSION) -> AppState:
    try:
        if app_state := db.get_app_state_info(APP_VERSION):
            return AppState(*app_state)
        db.add_app_state_info(APP_VERSION)
        return AppState(*db.get_app_state_info(APP_VERSION))
    except Exception as e:
        print('Ошибка в _get_app_state_info()', e)
        return None