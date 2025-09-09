from celery import shared_task
from cashier.models import Payment
from time import sleep
from decimal import Decimal
import requests
from datetime import datetime

# def check_tron(wallet_address, from_timestamp, amount_usdt):
#     api_url = f"https://apilist.tronscan.org/api/transaction"
#     params = {
#         "address": wallet_address,
#         "limit": 100,
#         "sort": "-timestamp"
#     }

#     try:
#         response = requests.get(api_url, params=params)
#         response.raise_for_status()
#         transactions = response.json().get("data", [])
#         for tx in transactions:
#             if tx["tokenTransferInfo"]["symbol"] == "USDT" and \
#                tx["tokenTransferInfo"]["amount_str"] == str(amount_usdt * 10**6) and \
#                tx["timestamp"] >= from_timestamp:
#                 return True
#         return False
#     except requests.RequestException as e:
#         print(f"Ошибка запроса: {e}")
#         return False

# def check_eth(payment):
#     return Decimal(0)

# def check_bch(payment):
#     return Decimal(0)

@shared_task
def my_task():
    Payment.fetch_payments()