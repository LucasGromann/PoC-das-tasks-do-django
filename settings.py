INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "myapp",
]

CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Sao_Paulo"

TASKS = {
    "default": {
        "BACKEND": "django_celery_task_backend.backend.CeleryTaskBackend",
        "OPTIONS": {
            "default_queue": "default",
        },
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://localhost:6379/1",
    }
}