from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.db import models
from django.db.models import Sum, Count
from decimal import Decimal
from django.utils.timezone import now
from datetime import timedelta
import random

# Список API токенов для Moralis
MORALIS_API_TOKENS = [
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjZiOTk1YzlkLTdmZDMtNDA2ZS1hNzljLTdmMzk0YzkyNTlkMyIsIm9yZ0lkIjoiNDM4Mzg3IiwidXNlcklkIjoiNDUxMDAzIiwidHlwZUlkIjoiNjg1YTIzZWQtYWJiYS00M2FkLWE3MTMtMDM2Y2M2ZTViODFhIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3NDMwOTczNzQsImV4cCI6NDg5ODg1NzM3NH0.bBCGSklLK2FomoduHuKidt2FGcN1bxCmoZSAbFBdqeA",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImUwYjE3ZjczLTc1ZTAtNGQ3Yi1iMzhhLTc3OTI2YTA2OWU3NSIsIm9yZ0lkIjoiNDM4NTIxIiwidXNlcklkIjoiNDUxMTQ2IiwidHlwZUlkIjoiZjdlODNiYzEtZGMyZC00M2JmLTgwNWUtZmVhNDY4MjQ5YTI1IiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3NDMxNzMxNzIsImV4cCI6NDg5ODkzMzE3Mn0.LPvq3zvvkEQinkWaBfNHj1SbvMvqlIvKllYxEEBiCac",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjE2NTI4NTA1LTBiY2ItNDViZS1hZTU2LTU4MTQyOTlkMDU1NCIsIm9yZ0lkIjoiNDM4NTIzIiwidXNlcklkIjoiNDUxMTQ4IiwidHlwZUlkIjoiYjNlN2UwOGMtZTE5Yi00ZmQzLTk0ZDUtNjA5OTllMTZlYjJkIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3NDMxNzM0MTMsImV4cCI6NDg5ODkzMzQxM30.etXV4yjCzAhOmwab0Yh7_ZK6Uqm6rcT3AluNO0BIRUQ",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImQ1NjY5YjU0LTljYmUtNDMwZC04MGRjLWFiOTZlNWRjZGNhOSIsIm9yZ0lkIjoiNDM4NTI0IiwidXNlcklkIjoiNDUxMTQ5IiwidHlwZUlkIjoiZDQ3Nzc5MjktYWVlNy00NGU0LTlhYTItYWRmMjg0NjY1NzQyIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3NDMxNzM0NjgsImV4cCI6NDg5ODkzMzQ2OH0.ktp5jRjVDwJHzw1ZiuARHcy1YukNO5hhX35K2cqvlGM",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjYxZDNjMGQxLWY4MzYtNDAzZC05ZDU0LWEzZmUyNzU0Mzc0NiIsIm9yZ0lkIjoiNDM4NTI1IiwidXNlcklkIjoiNDUxMTUwIiwidHlwZUlkIjoiZTVkMjU1OTctYjYzMS00YjlkLThlMTgtZjI1YjU1MDBlYWIxIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3NDMxNzM1MTgsImV4cCI6NDg5ODkzMzUxOH0.bz67EdneluzewaAm9tEnW6kFTH53mOdY0Qywp2Zkr5U"
]

def get_random_api_token():
    """Функция для получения случайного API токена из списка"""
    return random.choice(MORALIS_API_TOKENS)

class Token(models.Model):
    name = models.CharField(max_length=64)
    code = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.name}"

class Network(models.Model):
    name = models.CharField(max_length=64)
    code = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.name}"

class CashRegister(models.Model):
    name = models.CharField(max_length=512, null=True, blank=True)
    
    def open(self):
        total_price = 0
        total_count = 0
        for cashier in self.cashiers.all():
            data =  cashier.user.payments.filter(status='open').aggregate(
                total_price=Sum('price'),
                total_count=Count('id')
            )
            total_price = data.get('total_price', 0)
            total_count = data.get('total_count', 0)
        return f"({total_count}) / {total_price} USDT"

    def closed(self):
        total_price = 0
        total_count = 0
        for cashier in self.cashiers.all():
            data =  cashier.user.payments.filter(status='closed').aggregate(
                total_price=Sum('price'),
                total_count=Count('id')
            )
            total_price = data.get('total_price', 0)
            total_count = data.get('total_count', 0)
        return f"({total_count}) / {total_price} USDT"
    
    def payed(self):
        total_price = 0
        total_count = 0
        for cashier in self.cashiers.all():
            data =  cashier.user.payments.filter(status='payed').aggregate(
                total_price=Sum('payed'),
                total_count=Count('id')
            )
            total_price = data.get('total_price', 0)
            total_count = data.get('total_count', 0)
        return f"({total_count}) / {total_price} USDT"


    def __str__(self):
        return f"{self.name}"


class Wallet(models.Model):
    cash_register = models.ForeignKey(CashRegister, on_delete=models.CASCADE, related_name="wallets")
    address = models.CharField(max_length=1024)
    network = models.ForeignKey(Network, on_delete=models.CASCADE, related_name="wallets")
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="wallets", null=True, blank=False)
    
    def __str__(self):
        return f"{self.network.name}"

class Cashier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    cash_register = models.ForeignKey(CashRegister, on_delete=models.CASCADE, related_name='cashiers', null=False, blank=False, default=None)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    def open(self):
        data =  self.user.payments.filter(status='open').aggregate(
            total_price=Sum('price'),
            total_count=Count('id')
        )
        return f"({data.get('total_count', 0)}) / {data.get('total_price', 0)} USDT"

    def closed(self):
        data =  self.user.payments.filter(status='closed').aggregate(
            total_price=Sum('price'),
            total_count=Count('id')
        )
        return f"({data.get('total_count', 0)}) / {data.get('total_price', 0)} USDT"
    
    def payed(self):
        data =  self.user.payments.filter(status='payed').aggregate(
            total_price=Sum('payed'),
            total_count=Count('id')
        )
        return f"({data.get('total_count', 0)}) / {data.get('total_price', 0)} USDT"


class Payment(models.Model):
    STATUSES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('payed', 'Paid'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments', null=True, default=None, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    status = models.CharField(choices=STATUSES, max_length=30, default='open')
    payed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    def cashier(self):
        return f"{self.user.profile.cash_register}"
    
    def address(self):
        name = {
            1 : "TRON",
            2 : "ETH",
            3 : "BSC"
        }
        if self.wallet is not None and self.wallet.address is not None and len(self.wallet.address) > 10:
            return self.wallet.address[:4] + "..." + self.wallet.address[-6:] + " " + name[self.wallet.network.code]
        else:
            return 'Not set'
    
    def cryptocurrency(self):
        if self.wallet is not None and self.wallet.address is not None:
            return self.wallet.token.name
        else:
            return 'Not set'
    
    def total(self):
        price = Decimal(0)
        for tip in self.tips.all():
            price += tip.price
        return self.price + price
    
    def fetch_payments():
        print("START")
        for payment in Payment.objects.filter(status='open').all():
            try:
                # Проверяем, есть ли у платежа кошелек и токен
                if payment.wallet and payment.wallet.token:
                    # Проверяем USDT токены
                    if payment.wallet.token.name == "USDT" or payment.wallet.token.name == "Tether USD":
                        if payment.wallet.network.code == 2:  # ETH
                            payment.get_payed_eth_usdt()
                        elif payment.wallet.network.code == 3:  # BSC
                            payment.get_payed_bsc_usdt()
                    # Проверяем USDC токены
                    elif payment.wallet.token.name == "USDC" or payment.wallet.token.name == "USD Coin":
                        payment.get_payed_usdc()
            except Exception as err:
                print("Exception:", err)
            payment.close_timeleft_payment()

    def close_timeleft_payment(self):
        if now() >= self.created_at + timedelta(minutes=10):
            self.status = "closed"
            self.save()
    
    def get_payed_bsc_usdt(self):
        from moralis import evm_api
        from django.utils.timezone import localtime
        from pytz import UTC

        api_key = get_random_api_token()

        utc_time = self.updated_at.astimezone(UTC)
        start_timestamp = utc_time.strftime('%Y-%m-%d %H:%M:%S')

        print(start_timestamp, self.updated_at)

        params = {
        "chain": "bsc",
        "contract_addresses": [
            "0x55d398326f99059fF775485246999027B3197955"
        ],
        "from_date": start_timestamp,
        "limit": 1,
        "order": "DESC",
        "address": self.wallet.address
        }

        result = evm_api.token.get_wallet_token_transfers(
            api_key=api_key,
            params=params,
        )
        if(len(result['result'])> 0):
            payed = Decimal(result['result'][0]['value_decimal'])
            self_payed = self.payed if self.payed is not None else Decimal(0)
            self.payed = payed + self_payed

            if self.payed >= self.price:
                self.status = 'payed'
            self.save()
    
    def get_payed_eth_usdt(self):
        from moralis import evm_api
        from django.utils.timezone import localtime
        from pytz import UTC

        api_key = get_random_api_token()

        utc_time = self.updated_at.astimezone(UTC)
        start_timestamp = utc_time.strftime('%Y-%m-%d %H:%M:%S')

        print(start_timestamp, self.updated_at)

        params = {
        "chain": "eth",
        "contract_addresses": [
            "0xdAC17F958D2ee523a2206206994597C13D831ec7"
        ],
        "from_date": start_timestamp,
        "limit": 1,
        "order": "DESC",
        "address": self.wallet.address
        }

        result = evm_api.token.get_wallet_token_transfers(
            api_key=api_key,
            params=params,
        )
        if(len(result['result'])> 0):
            payed = Decimal(result['result'][0]['value_decimal'])
            self_payed = self.payed if self.payed is not None else Decimal(0)
            self.payed = payed + self_payed

            if self.payed >= self.price:
                self.status = 'payed'
            self.save()

    def get_payed_usdc(self):
        from moralis import evm_api
        from django.utils.timezone import localtime
        from pytz import UTC

        api_key = get_random_api_token()

        utc_time = self.updated_at.astimezone(UTC)
        start_timestamp = utc_time.strftime('%Y-%m-%d %H:%M:%S')

        print(f"Checking USDC payment for {self.wallet.address} on {self.wallet.network.name}")

        chain = "eth"
        contract_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        print('self.wallet.network.code', self.wallet.network.code)
        if self.wallet.network.code == 3:  # BSC
            chain = "bsc"
            contract_address = "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d"
        # elif self.wallet.network.code == 137:  # Polygon
        #     chain = "polygon"
        #     contract_address = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"  # USDC на Polygon
        # elif self.wallet.network.code == 43114:  # Avalanche
        #     chain = "avalanche"
        #     contract_address = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"  # USDC на Avalanche

        params = {
            "chain": chain,
            "contract_addresses": [contract_address],
            "from_date": start_timestamp,
            "limit": 1,
            "order": "DESC",
            "address": self.wallet.address
        }

        print('params', params)

        result = evm_api.token.get_wallet_token_transfers(
            api_key=api_key,
            params=params,
        )
        print('result', result)
        if(len(result['result']) > 0):
            payed = Decimal(result['result'][0]['value_decimal'])
            self_payed = self.payed if self.payed is not None else Decimal(0)
            self.payed = payed + self_payed

            print(f"USDC payment detected: {payed} USDC")

            if self.payed >= self.price:
                self.status = 'payed'
            self.save()
            

class Tip(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='tips')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



# import requests
# from datetime import datetime

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

# Также нужно отслеживать добавление/удаление кассиров к кассе
@receiver(post_save, sender=Cashier)
def assign_group_to_new_cashier(sender, instance, created, **kwargs):
    """
    Добавляет группу 'CASHIER' к новому кассиру
    и устанавливает is_staff=True
    """
    print('cashier_group, user.groups.all()', kwargs.get('update_fields'))
    if created or kwargs.get('update_fields'):
        # Получаем или создаем группу CASHIER
        cashier_group, created = Group.objects.get_or_create(name='CASHIER')
        
        user = instance.user
        
        # Проверяем, есть ли у пользователя группа CASHIER
        print(cashier_group, user.groups.all())
        if cashier_group not in user.groups.all():
            # Добавляем группу
            user.groups.add(cashier_group)
            
            # Устанавливаем флаг is_staff
            user.is_staff = True
            user.save()
            print(f"Пользователь {user.username} добавлен в группу CASHIER и is_staff=True")


@receiver(post_save, sender=CashRegister)
def assign_cashier_group(sender, instance, created, **kwargs):
    """
    Добавляет группу 'CASHIER' к пользователям кассиров 
    и устанавливает is_staff=True
    """
    # Получаем или создаем группу CASHIER
    cashier_group, created = Group.objects.get_or_create(name='CASHIER')
    print('assign_cashier_group', cashier_group)
    
    # Для всех кассиров данного кассового аппарата
    for cashier in instance.cashiers.all():
        user = cashier.user
        
        # Проверяем, есть ли у пользователя группа CASHIER
        if cashier_group not in user.groups.all():
            # Добавляем группу
            user.groups.add(cashier_group)
            
            # Устанавливаем флаг is_staff
            user.is_staff = True
            user.save()
            print('assign_cashier_group', user)
            print(f"Пользователь {user.username} добавлен в группу CASHIER и is_staff=True")
