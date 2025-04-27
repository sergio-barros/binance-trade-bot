import schedule
import time
import os
import datetime
from services.data_fetcher import get_klines, get_symbol_info
from trading.simple_strategy import simple_moving_average_strategy
from trading.executor import execute_order
from services.binance_client import client
from services.telegram_alert import send_telegram_message
from config import RUN_INTERVAL_MODE, MAX_DAILY_OPERATIONS, TAKE_PROFIT_PERCENT, STOP_LOSS_PERCENT
import csv
import logging

# Criar diretório de logs se não existir
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configurações
SYMBOLS = ["BTCUSDT", "ETHUSDT"]
USDT_TO_SPEND = {
    "BTCUSDT": 10.5,
    "ETHUSDT": 10.5
}

# Preço médio manual (opcional, para ativos que você já comprou manualmente)
INITIAL_AVERAGE_PRICES = {
    "BTCUSDT": 10.32,  # <-- Atualize aqui com seu preço real de compra
    "ETHUSDT": 10.28    # <-- Atualize aqui com seu preço real de compra
}


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler("logs/trading.log"),
        logging.StreamHandler()
    ]
)

# Variável global para contar operações do dia
daily_operations_count = 0
last_reset_date = datetime.date.today()
average_buy_prices = {}  # Guarda preço médio de compra por ativo

trade_history_file = "trades_history.csv"
def save_trade_history(timestamp, symbol, side, quantity, price, total_value):
    header = ["timestamp", "symbol", "side", "quantity", "price", "total_value"]
    data = [timestamp, symbol, side, quantity, price, total_value]

    file_exists = os.path.isfile(trade_history_file)

    with open(trade_history_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(data)

def get_current_price(symbol):
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker['price'])

def adjust_quantity(symbol, quantity):
    info = get_symbol_info(symbol)
    lot_size_filter = next(f for f in info['filters'] if f['filterType'] == 'LOT_SIZE')
    step_size = float(lot_size_filter['stepSize'])
    adjusted_quantity = quantity - (quantity % step_size)
    return format(adjusted_quantity, '.8f')

def get_min_notional(symbol):
    info = get_symbol_info(symbol)
    for f in info['filters']:
        if f['filterType'] == 'MIN_NOTIONAL':
            return float(f['minNotional'])
    # Se o filtro não existir, assume 10.0 USDT como mínimo
    logging.warning(f"Filtro MIN_NOTIONAL não encontrado para {symbol}. Assumindo 10.0 USDT como mínimo.")
    return 10.0

def get_usdt_balance():
    account = client.get_account()
    for asset in account['balances']:
        if asset['asset'] == 'USDT':
            return float(asset['free'])
    return 0.0


def job():
    global daily_operations_count, last_reset_date

    current_date = datetime.date.today()
    if current_date != last_reset_date:
        logging.info("Resetando contador diário de operações.")
        daily_operations_count = 0
        last_reset_date = current_date

    if daily_operations_count >= MAX_DAILY_OPERATIONS:
        logging.warning(f"Limite máximo de {MAX_DAILY_OPERATIONS} operações diárias atingido. Nenhuma nova operação será realizada hoje.")
        return

    start_time = datetime.datetime.now()
    total_symbols = 0
    total_operations = 0

    try:
        # Carregar preços médios iniciais se existirem
        for symbol, initial_price in INITIAL_AVERAGE_PRICES.items():
            if symbol not in average_buy_prices:
                average_buy_prices[symbol] = initial_price
                logging.info(f"Preço médio inicial configurado para {symbol}: {initial_price:.4f} USDT")

        for symbol in SYMBOLS:
            total_symbols += 1
            logging.info(f"Executando estratégia para {symbol}...")
            data = get_klines(symbol=symbol)
            decision = simple_moving_average_strategy(data)
            logging.info(f"Decisão para {symbol}: {decision}")

            if decision == "buy":
                price = get_current_price(symbol)
                usdt_amount = USDT_TO_SPEND.get(symbol, 5)
                quantity = format(usdt_amount / price, '.6f')
                average_buy_prices[symbol] = price
                logging.info(f"Registrado preço médio de compra para {symbol}: {price:.4f} USDT")
                execute_order(symbol, decision, quantity)
                save_trade_history(datetime.datetime.now(), symbol, "buy", quantity, price, float(quantity) * price)
                daily_operations_count += 1
                total_operations += 1

            elif decision == "sell":
                if symbol not in average_buy_prices:
                    logging.info(f"Sem registro de preço médio para {symbol}. Ignorando venda.")
                    continue

                average_price = average_buy_prices[symbol]
                price = get_current_price(symbol)  # <-- BUSCAR o preço atual aqui!

                take_profit_price = average_price * (1 + TAKE_PROFIT_PERCENT/100)
                stop_loss_price = average_price * (1 - STOP_LOSS_PERCENT/100)

                if price >= take_profit_price:
                    logging.info(f"Take Profit atingido: {price:.4f} >= {take_profit_price:.4f} para {symbol}. Vendendo.")
                elif price <= stop_loss_price:
                    logging.warning(f"Stop Loss atingido: {price:.4f} <= {stop_loss_price:.4f} para {symbol}. Vendendo.")
                else:
                    logging.info(f"Nenhuma condição de venda atingida para {symbol}. (Preço atual: {price:.4f})")
                    continue
                
                # 🔥 Cálculo correto do quantity ANTES de vender:
                usdt_amount = USDT_TO_SPEND.get(symbol, 1)
                raw_quantity = usdt_amount / price
                quantity = adjust_quantity(symbol, raw_quantity)
                logging.info(f"Vendendo {symbol} | Preço atual {price:.4f} USDT | Preço médio {average_price:.4f} USDT")
                execute_order(symbol, decision, quantity)
                save_trade_history(datetime.datetime.now(), symbol, "sell", quantity, price, float(quantity) * price)
                daily_operations_count += 1
                total_operations += 1


                if daily_operations_count >= MAX_DAILY_OPERATIONS:
                    logging.warning(f"Limite máximo de {MAX_DAILY_OPERATIONS} operações diárias atingido durante a execução.")
                    break
            else:
                logging.info(f"Nenhuma ação necessária para {symbol}: HOLD")

    except Exception as e:
        import traceback
        error_message = f"Erro geral no job:\n{traceback.format_exc()}"
        logging.error(error_message)
        send_telegram_message(error_message, critical=True)

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()

    summary_message = f"Resumo do ciclo: {total_symbols} ativos analisados, {total_operations} operações executadas, tempo de execução: {duration:.2f} segundos"
    logging.info(summary_message)

def send_daily_summary():
    total_trades = 0
    profit_loss = 0.0

    if not os.path.exists(trade_history_file):
        return

    with open(trade_history_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            total_trades += 1
            if row['side'] == 'sell':
                profit_loss += float(row['total_value'])
            elif row['side'] == 'buy':
                profit_loss -= float(row['total_value'])

    summary_message = f"Resumo diário:\nOperações: {total_trades}\nResultado estimado: {profit_loss:.2f} USDT"
    send_telegram_message(summary_message)

schedule.every().day.at("23:59").do(send_daily_summary)

# Controle de intervalo via .env
if RUN_INTERVAL_MODE.upper() == "FAST":
    schedule.every(1).minutes.do(job)
else:
    schedule.every(15).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
