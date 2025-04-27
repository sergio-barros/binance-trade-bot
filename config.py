import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
RUN_INTERVAL_MODE = os.getenv("RUN_INTERVAL_MODE", "NORMAL")
MAX_DAILY_OPERATIONS = int(os.getenv("MAX_DAILY_OPERATIONS", 10))
TAKE_PROFIT_PERCENT = float(os.getenv("TAKE_PROFIT_PERCENT", 2))
STOP_LOSS_PERCENT = float(os.getenv("STOP_LOSS_PERCENT", 2))