import datetime
import time
from datetime import datetime, timedelta
from datetime import datetime

from binance.error import ClientError

from api_connect import UM_client
from dotenv import load_dotenv
import os
import requests
from binance_api import get_klines
from chart_create import find_significant_levels, plot_candlestick_with_levels
from alert_manager import send_alert
# Завантажити змінні з .env
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def format_sum(val):
    if val >= 1_000_000_000:
        return f"{val / 1_000_000_000:.2f}kkk"
    elif val >= 1_000_000:
        return f"{val / 1_000_000:.2f}kk"
    elif val >= 100_000:
        return f"{val / 1_000:.0f}k"
    elif val >= 10_000:
        return f"{val / 1_000:.0f}k"
    elif val >= 1_000:
        return f"{val / 1_000:.0f}k"
    else:
        return f"{val:.0f}"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"❌ Error sending message to Telegram: {e}")

import threading
import time

message_buffer = []
buffer_lock = threading.Lock()
SEND_INTERVAL = 5  # Кожні 5 секунд
MAX_MESSAGE_LENGTH = 4000  # Безпечна межа, трохи нижче 4096


def buffer_worker():
    while True:
        time.sleep(SEND_INTERVAL)
        with buffer_lock:
            if message_buffer:
                # Об'єднуємо всі повідомлення
                combined_msg = "\n".join(message_buffer)
                message_buffer.clear()

                # Якщо довше за ліміт — розбити
                for i in range(0, len(combined_msg), MAX_MESSAGE_LENGTH):
                    chunk = combined_msg[i:i+MAX_MESSAGE_LENGTH]
                    send_telegram_message(chunk)

# Запустити окремий потік
threading.Thread(target=buffer_worker, daemon=True).start()

def add_to_buffer(text):
    with buffer_lock:
        message_buffer.append(text)


def pumpFound1(timeToChange=2, procent=1, ignor=5):
    """
    :param timeToChange: час за який має змінитись
    :param procent: відсотки на які має змінитись
    :param ignor: час ігнорування монети перед повторним прінтом
    :return: все виводить прінтами
    """
    msg = f"Pump Founder: Time - {timeToChange}min. Change - {procent}%"
    add_to_buffer(msg)
    print(msg)
    dbSize = int(((timeToChange * 60) / 3) * -1)


    def getTickerUM():
        data = UM_client.ticker_price() # функція бінанса поертає 278 >> {'symbol': 'TOMOUSDT', 'price': '1.2792', 'time': 1699952397314}

        parsed_data = data
        num = 0
        for n in parsed_data:
            num += 1
            #print(f"{num} >> {n}")
        return data


    result_list = []
    print_info = {}
    def check_price_change(symbol, new_price, old_price, timestamp):
        old_price = float(old_price)
        new_price = float(new_price)

        percent_change = ((new_price - old_price) / old_price) * 100

        # Перевірка, чи пройшло менше 2 хв від останнього прінта для цього символу
        if symbol in print_info and (datetime.now() - print_info[symbol]["last_print_time"]).seconds < ignor * 60:
            return  # Якщо так, то виходимо з функції без виконання прінта

        timestamp_formatted = datetime.fromtimestamp(timestamp / 1000).strftime("%H:%M:%S")
        def f_len_str(info, size):
            if len(info) < size:
                info += (' ' * (size - len(info)))
                return info
            return info

        if abs(percent_change) >= procent:
            if percent_change > 0:
                if symbol not in print_info:
                    print_info[symbol] = {"count": 0, "last_print_time": None}

                print_info[symbol]["count"] += 1
                count = print_info[symbol]["count"]
                print_info[symbol]["last_print_time"] = datetime.now()
                symbol = f_len_str(symbol, 13)
                print(f"{timestamp_formatted}   {symbol} Ціна {percent_change:.2f}%  {old_price}  >>>  {new_price}  Сигнал: {count} https://www.coinglass.com/tv/Binance_{symbol}")
                msg = (f"[🟢{symbol}](https://www.coinglass.com/tv/Binance_{symbol})  Ціна {percent_change:.2f}%  {old_price}  >>>  {new_price}  Сигнал: {count}")
                add_to_buffer(msg)
            else:
                if symbol not in print_info:
                    print_info[symbol] = {"count": 0, "last_print_time": None}

                print_info[symbol]["count"] += 1
                count = print_info[symbol]["count"]
                print_info[symbol]["last_print_time"] = datetime.now()
                symbol = f_len_str(symbol, 13)
                print(f"{timestamp_formatted}   {symbol} Ціна {percent_change:.2f}%  {old_price}  >>>  {new_price}  Сигнал: {count} https://www.coinglass.com/tv/Binance_{symbol}")
                msg = (f"[🔴{symbol}](https://www.coinglass.com/tv/Binance_{symbol})  Ціна {percent_change:.2f}%  {old_price}  >>>  {new_price}  Сигнал: {count}")
                add_to_buffer(msg)

    def foundPumpFn():
        while True:
            try:
                data = getTickerUM()

                for new_data in data:
                    found = False
                    for item_list in result_list:
                        if item_list[0]['symbol'] == new_data['symbol']:
                            old_price = item_list[-1]['price']
                            timestamp = item_list[-1]['time']
                            item_list.append(new_data)
                            check_price_change(new_data['symbol'], new_data['price'], old_price, timestamp)
                            # Залишаємо тільки останні три елементи у списку
                            item_list[:dbSize] = []
                            found = True
                            break
                    if not found:
                        result_list.append([new_data])

                #print(result_list)
                time.sleep(3)
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] API не відповідає або немає інтернету: {e}")
                print("Очікуємо 10 секунд перед наступною спробою...")
                time.sleep(10)  # Затримка перед наступною спробою


    foundPumpFn()

def pumpFound(timeToChange=2, procent=1, ignor=5):
    """
    :param timeToChange: час за який має змінитись
    :param procent: відсотки на які має змінитись
    :param ignor: час ігнорування монети перед повторним прінтом
    :return: все виводить прінтами
    """
    msg = f"Pump Founder: Time - {timeToChange}min. Change - {procent}%"
    add_to_buffer(msg)
    print(msg)

    dbSize = int(((timeToChange * 60) / 3) * -1)
    result_dict = {}  # symbol -> list of recent data
    print_info = {}   # symbol -> {count, last_print_time}

    def getTickerUM():
        from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
        res = UM_client.ticker_price()  # [{'symbol': 'BTCUSDT', 'price': '12345.67', 'time': 1699952397314}, ...]
        #print(res)
        #d = UM_client.index_info()
        d = UM_client.exchange_info()
        print(d)
        return res


    def check_price_change(symbol, new_price, old_price, timestamp):

        new_price = float(new_price)
        old_price = float(old_price)
        percent_change = ((new_price - old_price) / old_price) * 100

        now = datetime.now()
        try:
            if symbol in print_info and (now - print_info[symbol]["last_print_time"]).seconds < ignor * 60:
                return
        except Exception:
            return

        timestamp_formatted = datetime.fromtimestamp(timestamp / 1000).strftime("%H:%M:%S")
        symbol_str = symbol.ljust(13)

        if abs(percent_change) >= procent:
            if symbol not in print_info:
                print_info[symbol] = {"count": 0, "last_print_time": None}

            INTERVAL = "5m"
            LIMIT = 500
            chart_path = f"charts/{symbol}.png"

            try:

                df = get_klines(f"{symbol}", interval=INTERVAL, limit=LIMIT)
            except ClientError as e:
                print(f"Помилка Binance API для символу {symbol}: {e}")
                return
            # current_price = df.iloc[-1]['close']
            if len(df) < LIMIT * 0.5:
                return

            print_info[symbol]["count"] += 1
            print_info[symbol]["last_print_time"] = now
            count = print_info[symbol]["count"]

            color = "🟢" if percent_change > 0 else "🔴"
            url = f"https://www.coinglass.com/tv/Binance_{symbol}"
            print(f"{timestamp_formatted}   {symbol_str} Ціна {percent_change:.2f}%  {old_price}  >>>  {new_price}  Сигнал: {count} {url}")
            #msg = f"[{color}{symbol}](https://www.coinglass.com/tv/Binance_{symbol}) {percent_change:.2f} %  {old_price} > {new_price}  Сигнал: {count} | {timeToChange}min{procent}%"
###########################################################################
            msg = {
                "link": f"<a href='https://www.coinglass.com/tv/Binance_{symbol}'>{color}{symbol}</a>", #f"[{color}{symbol}](https://www.coinglass.com/tv/Binance_{symbol})",
                "percent_change":f"{percent_change:.2f} %",
                "change_price": f"{old_price} > {new_price}",
                "signal":f"Сигнал: {count} |",
                "config":f"{timeToChange}min{procent}% ",
                "hashtag": f"#{symbol}"
            }

            levels, alines = find_significant_levels(df, order=25, min_diff_percent=1, max_crossings=2, lookback=5, )

            plot_candlestick_with_levels(df, symbol, interval=INTERVAL ,save_path=chart_path, alines=alines)
            send_alert(symbol, msg, chart_path)







            #add_to_buffer(msg)

    def foundPumpFn():
        while True:
            try:
                data = getTickerUM()
                for new_data in data:
                    symbol = new_data['symbol']
                    new_price = new_data['price']
                    timestamp = new_data.get('time', int(time.time() * 1000))  # fallback, якщо час відсутній

                    if symbol not in result_dict:
                        result_dict[symbol] = []

                    old_price = result_dict[symbol][-1]['price'] if result_dict[symbol] else new_price
                    old_timestamp = result_dict[symbol][-1]['time'] if result_dict[symbol] else timestamp

                    result_dict[symbol].append(new_data)
                    result_dict[symbol] = result_dict[symbol][dbSize:]

                    check_price_change(symbol, new_price, old_price, old_timestamp)

                time.sleep(3)
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] API не відповідає або немає інтернету: {e}")
                print("Очікуємо 10 секунд перед наступною спробою...")
                time.sleep(10)

    foundPumpFn()