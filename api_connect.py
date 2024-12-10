from binance.spot import Spot
from binance.um_futures import UMFutures
from dotenv import load_dotenv
import os

# Завантаження змінних з .env файлу
load_dotenv()

# Використання змінних середовища
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")



client = Spot()


client = Spot(
    api_key=api_key,
    api_secret=api_secret
)

UM_client = UMFutures()

UM_client = UMFutures(
    key=api_key,
    secret=api_secret
)
