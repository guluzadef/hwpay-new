from django.contrib import admin
from django.urls import path, include
from .views import payment, tips, custom_tip, generate_qr, index, check_payment, payment_type, close

urlpatterns = [
    path('', index),
    path('payment-type/<int:id>', payment_type),
    path('tips/<int:id>/<str:coin>/<int:wallet_id>', tips),
    path('custom-tip/<int:id>', custom_tip),
    path('payment/<int:id>/<int:tip>', payment),
    path('payment/<int:id>/<str:tip>/<str:types>', payment),
    path('close/<int:id>', close),
    path('generate_qr/<int:id>', generate_qr, name='generate_qr'),
    path('check-payment/<int:id>', check_payment),
]
