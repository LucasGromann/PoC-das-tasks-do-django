import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

app = Celery("myproject")

# Lê as configs com prefixo CELERY_ do settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# Descobre tasks automaticamente em cada app instalada
app.autodiscover_tasks()


