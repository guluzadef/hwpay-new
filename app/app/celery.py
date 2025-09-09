# your_project/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Устанавливаем настройки Django по умолчанию
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')

# Используем строку для задания конфигурации брокера
# Для простоты использования Redis в качестве брокера
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем задачи в каждом из зарегистрированных приложений Django
app.autodiscover_tasks()
