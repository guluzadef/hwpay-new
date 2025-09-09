from django.shortcuts import render, redirect
from cashier.models import Payment, Tip, Wallet
import qrcode
from io import BytesIO
from django.http import HttpResponse
from decimal import Decimal
from django.http import JsonResponse
from cashier.models import Token

def index(request):
    return redirect('/admin')

def payment_type(request, id):
    payment = Payment.objects.get(pk=id)
    print('------------', payment.price)
    cash_register = request.user.profile.cash_register
    wallets = Wallet.objects.filter(
        cash_register=cash_register
    )
    tokens = Token.objects.all()
    return render(request, "payment/payment-type.html", context={'payment': payment, 'wallets': wallets, 'timer': payment.created_at.isoformat().replace(' ', 'T'), 'tokens': tokens})

def tips(request, id, coin, wallet_id):
    payment = Payment.objects.get(pk=id)
    wallet = Wallet.objects.get(pk=wallet_id)
    payment.wallet = wallet
    payment.save()
    print('------------', payment.price)
    return render(request, "payment/tips.html", context={'payment': payment})

def custom_tip(request, id):
    payment = Payment.objects.get(pk=id)
    print('------------', payment.price)
    return render(request, "payment/custom-tip.html", context={'payment': payment})

def close(request, id):
    payment = Payment.objects.get(pk=id)
    if payment.status == 'open':
        payment.status = 'closed'
        payment.save()
    return JsonResponse({"status": payment.status})

def payment(request, id, tip, types='percent'):
    payment = Payment.objects.get(pk=id)
    print('------------', id, tip)
    if types == 'custom':
        tip_price = round(Decimal(tip), 2)
    else:
        tip_price = round(payment.price*Decimal(int(tip)/100), 2)

    tip_model = Tip.objects.get_or_create(
        payment_id = id, 
    )[0]
    tip_model.price = tip_price
    tip_model.save()
    return render(request, "payment/index.html", context={'payment': payment, 'tip': tip_model, 'total': payment.total()})

def generate_qr(request, id):
    payment = Payment.objects.get(pk=id)
    data = payment.wallet.address
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Создание изображения
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return HttpResponse(buffer, content_type="image/png")


def check_payment(request, id):
    payment = Payment.objects.get(pk=id)
    data = {
        "result": payment.status=='payed'
    }
    return JsonResponse(data)
