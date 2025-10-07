# settings_manager.py
import database
SETTINGS = {}

def load_settings():
    """Barcha sozlamalarni bazadan o'qib, xotiraga yuklaydi."""
    global SETTINGS
    print("Sozlamalar yuklanmoqda...")
    keys = ['telegram_token', 'telegram_chat_id', 'company_name', 'ip_filtering_enabled']
    for key in keys:
        SETTINGS[key] = database.get_setting(key, '')
    print("Sozlamalar muvaffaqiyatli yuklandi.")

def get(key, default=None):
    return SETTINGS.get(key, default)