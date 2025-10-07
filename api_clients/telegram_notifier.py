# api_clients/telegram_notifier.py

import requests
import settings_manager # Sozlamalarni markazlashgan holda olish uchun

def send_telegram_message(message: str) -> bool:
    """
    Sozlamalarda ko'rsatilgan Telegram chatiga xabar yuboradi.
    
    Args:
        message (str): Yuboriladigan xabar matni. HTML teglarni ishlata oladi.

    Returns:
        bool: Xabar muvaffaqiyatli yuborilsa True, aks holda False qaytaradi.
    """
    # Sozlamalarni settings_manager orqali olamiz
    token = settings_manager.get('telegram_token')
    chat_id = settings_manager.get('telegram_chat_id')

    # Token yoki chat_id kiritilmagan bo'lsa, funksiyani to'xtatamiz va xatolikni konsolga chiqaramiz
    if not token or not chat_id:
        print("XATO: Telegram token yoki chat ID sozlamalarda kiritilmagan.")
        return False

    # Telegram Bot API manzili
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Yuboriladigan ma'lumotlar
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'  # Xabarni qalin (<b>), yotiq (<i>) yoki link (<a>) qilish imkonini beradi
    }

    try:
        # API ga 10 soniyalik kutish vaqti bilan so'rov yuborish
        response = requests.post(url, data=payload, timeout=10)
        # Agar server xatolik statusini qaytarsa (masalan, 401, 404, 500), exception ko'taradi
        response.raise_for_status()

        # Javobni tekshirish
        result = response.json()
        if result.get('ok'):
            print(f"Telegramga xabar muvaffaqiyatli yuborildi.")
            return True
        else:
            # Agar API "ok: false" qaytarsa (masalan, chat topilmasa)
            print(f"Telegram API xatoligi: {result.get('description')}")
            return False

    except requests.exceptions.RequestException as e:
        # Internetga ulanish, DNS yoki boshqa tarmoq xatoliklari
        print(f"Telegramga xabar yuborishda tarmoq xatoligi yuz berdi: {e}")
        return False