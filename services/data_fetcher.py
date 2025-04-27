from .binance_client import client

def get_klines(symbol="BTCUSDT", interval="15m", limit=100):
    return client.get_klines(symbol=symbol, interval=interval, limit=limit)

def get_symbol_info(symbol):
    return client.get_symbol_info(symbol)