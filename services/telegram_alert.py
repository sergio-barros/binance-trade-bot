import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message, critical=False):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    prefix = "\u26a0\ufe0f [CRÍTICO] " if critical else "\u2139\ufe0f [INFO] "
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": prefix + message
    }
    requests.post(url, data=payload)