import datetime
import time
from datetime import datetime, timedelta
from datetime import datetime
from api_connect import UM_client


def pumpFound(timeToChange=2, procent=1, ignor=5):
    """
    :param timeToChange: час за який має змінитись
    :param procent: відсотки на які має змінитись
    :param ignor: час ігнорування монети перед повторним прінтом
    :return: все виводить прінтами
    """
    print(f"Pump Founder: Time - {timeToChange}min. Change - {procent}%")
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
            else:
                if symbol not in print_info:
                    print_info[symbol] = {"count": 0, "last_print_time": None}

                print_info[symbol]["count"] += 1
                count = print_info[symbol]["count"]
                print_info[symbol]["last_print_time"] = datetime.now()
                symbol = f_len_str(symbol, 13)
                print(f"{timestamp_formatted}   {symbol} Ціна {percent_change:.2f}%  {old_price}  >>>  {new_price}  Сигнал: {count} https://www.coinglass.com/tv/Binance_{symbol}")


    def foundPumpFn():
        while True:
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



    foundPumpFn()