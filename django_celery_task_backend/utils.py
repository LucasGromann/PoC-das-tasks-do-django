from django.core.cache import cache
from django.utils.module_loading import import_string

CACHE_PREFIX = "celery_tasks_backend:"
CACHE_TTL = 60 * 60 * 24 


def store_task_mapping(result_id: str, task_path: str):
    cache.set(f"{CACHE_PREFIX}{result_id}", task_path, CACHE_TTL)


def get_task_from_result_id(result_id: str):
    task_path = cache.get(f"{CACHE_PREFIX}{result_id}")
    if not task_path:
        return None
    return import_string(task_path)

