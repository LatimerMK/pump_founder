import websocket
import json
from itertools import permutations

import logging
from logging.handlers import TimedRotatingFileHandler

# Налаштування логування
logger = logging.getLogger("AsyncLogger")
logger.setLevel(logging.DEBUG)

# Хендлер для запису в файл з ротацією по даті
log_file = "app.log"  # Вказуємо файл без папки
handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7, encoding="utf-8")
handler.suffix = "%Y-%m-%d"  # Додаємо дату в назву файлу логів
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

# Додаємо хендлер до логера
logger.addHandler(handler)

# Вивід логів у консоль з кольоровим форматуванням
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
logger.addHandler(console_handler)

# Список торгових пар
symbols = ["fdusdusdt", "fdusdusdc", "usdcusdt"]

# Збереження останніх котирувань
prices = {}


def on_message(ws, message):
    data = json.loads(message)
    symbol = data['s'].lower()
    prices[symbol] = {"bid": float(data['b']), "ask": float(data['a'])}

    if all(sym in prices for sym in symbols):
        check_arbitrage()


def check_arbitrage():
    routes = [
        ["fdusdusdt", "fdusdusdc", "usdcusdt"],
        ["fdusdusdt", "usdcusdt", "fdusdusdc"],
        ["fdusdusdc", "fdusdusdt", "usdcusdt"],
        ["fdusdusdc", "usdcusdt", "fdusdusdt"],
        ["usdcusdt", "fdusdusdt", "fdusdusdc"],
        ["usdcusdt", "fdusdusdc", "fdusdusdt"]
    ]

    asset_map = {
        "fdusdusdt": ("USDT", "FDUSD"),
        "fdusdusdc": ("FDUSD", "USDC"),
        "usdcusdt": ("USDC", "USDT")
    }

    start_usdt = 100  # Початковий об'єм у USDT
    best_profit = float('-inf')
    best_route = None

    for route in routes:
        amount = start_usdt
        asset_flow = ["USDT"]
        for pair in route:
            if pair == "fdusdusdt":
                amount /= prices[pair]["ask"]  # Купівля FDUSD
            elif pair == "fdusdusdc":
                amount *= prices[pair]["bid"]  # Продаж FDUSD за USDC
            elif pair == "usdcusdt":
                amount *= prices[pair]["bid"]  # Продаж USDC за USDT
            asset_flow.append(asset_map[pair][1])

        profit = amount - start_usdt
        if profit > best_profit:
            best_profit = profit
            best_route = asset_flow

    #print(f"Найкращий маршрут: {' -> '.join(best_route)}")
    if best_profit < 0:
        logger.info(f"Найкращий маршрут: {' -> '.join(best_route)} - Очікуваний результат: {start_usdt + best_profit:.2f} USDT (прибуток: {best_profit:.4f} USDT)")

def on_error(ws, error):
    logger.error(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    logger.info("Closed")

def on_open(ws):
    payload = {"method": "SUBSCRIBE", "params": [f"{symbol}@bookTicker" for symbol in symbols], "id": 1}
    ws.send(json.dumps(payload))

ws = websocket.WebSocketApp(
    "wss://stream.binance.com:9443/ws",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
)
ws.on_open = on_open
ws.run_forever()
