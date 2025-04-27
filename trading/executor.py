from services.binance_client import client
from services.telegram_alert import send_telegram_message
import logging
import traceback

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler("logs/trading.log"),
        logging.StreamHandler()
    ]
)

def execute_order(symbol, side, quantity):
    try:
        order = client.create_order(
            symbol=symbol,
            side=side.upper(),
            type="MARKET",
            quantity=quantity
        )
        message = f"Ordem executada: {side.upper()} {quantity} {symbol}"
        logging.info(message)
        send_telegram_message(message)
        return order
    except Exception as e:
        error_message = f"Erro crítico ao executar ordem para {symbol}: {traceback.format_exc()}"
        logging.error(error_message)
        send_telegram_message(error_message, critical=True)
        return None