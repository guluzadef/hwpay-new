from django.contrib import admin
from .models import Cashier, Payment, CashRegister, Wallet, Network, Tip, Token
from django.utils.html import format_html

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name',)
    # readonly_fields = ('name', 'code')
    
    # def has_add_permission(self, request):
    #     return False
        
    # def has_delete_permission(self, request, obj=None):
    #     return False
        
    # def has_change_permission(self, request, obj=None):
    #     return False


# class PaymentForm(forms.ModelForm):
#     class Meta:
#         model = Payment
#         fields = ['user', 'price', 'status', 'wallet', 'payed']

#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user', None)  # Получаем пользователя из переданных данных
#         super().__init__(*args, **kwargs)

#         if user and hasattr(user, 'profile') and user.profile.cash_register:
#             self.fields['wallet'].queryset = Wallet.objects.filter(
#                 cash_register=user.profile.cash_register
#             )
#         else:
#             self.fields['wallet'].queryset = Wallet.objects.none()

# class PaymentForm(forms.ModelForm):
#     class Meta:
#         model = Payment
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         # Получаем текущего пользователя из контекста
#         user = kwargs.pop('user', None)
#         super().__init__(*args, **kwargs)

#         # Фильтруем поле wallet на основе выбранного cash_register
#         if self.instance and self.instance.user:
#             self.fields['wallet'].queryset = Wallet.objects.filter(
#                 cash_register=self.instance.user.cash_register
#             )
#         elif user:
#             # Если создаётся новая запись, фильтруем кошельки на основе текущего пользователя
#             self.fields['wallet'].queryset = Wallet.objects.filter(
#                 cash_register__payments__user=user
#             )


class WalletInline(admin.TabularInline):
    model = Wallet
    extra = 0 
    min_num = 1

class CashierInline(admin.TabularInline):
    model = Cashier
    extra = 0 
    min_num = 1

@admin.register(CashRegister)
class CashRegisterAdmin(admin.ModelAdmin):
    list_display = ('name', 'open', 'closed', 'payed')
    inlines = [CashierInline, WalletInline]

@admin.register(Cashier)
class CashierAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'cash_register', 'open', 'closed', 'payed')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'cryptocurrency', 'price', 'created_at', 'payed', 'status', 'qr_code_for_payment')
    list_filter = (
        'status',
        'user',
        'created_at',
        'wallet__token',
        'wallet__network'
    )
    # search_fields = ('status', )
    fields = ('price', )
    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user
            # obj.wallet = request.user.profile.cash_register.wallet
        obj.save()
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser or request.user.groups.filter(name='ADMIN').exists():
            return qs

        return qs.filter(user=request.user)
    
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
        
    #     print('-------', request.user)
    #     if hasattr(request.user, 'profile') and request.user.profile.cash_register:
    #         cash_register = request.user.profile.cash_register
    #         form.base_fields['wallet'].queryset = Wallet.objects.filter(
    #             cash_register=cash_register
    #         )
    #     else:
    #         form.base_fields['wallet'].queryset = Wallet.objects.none()
        
    #     return form
        
    def qr_code_for_payment(self, obj):
        if obj.status == 'open':
            return format_html(f'<a href="/payment-type/{obj.id}" target="_blank"><img src="/static/qrcode-scan.png" alt="QR CODE" style="width:32px;height:32px;margin:5px 0 5px 0;"></a>')
        else:
            return ''

    qr_code_for_payment.short_description = 'QR Code For Payment'


@admin.register(Network)
class NetworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')

    # def has_add_permission(self, request):
    #     return False

    # def has_change_permission(self, request, obj=None):
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     return False


@admin.register(Tip)
class TipAdmin(admin.ModelAdmin):
    list_display = ('payment', 'price', 'created_at')

    # def has_add_permission(self, request):
    #     return False

    # def has_change_permission(self, request, obj=None):
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     return True