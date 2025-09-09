from django.contrib import admin
from .models import TestWebhook

@admin.register(TestWebhook)
class TestWebhookAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')
