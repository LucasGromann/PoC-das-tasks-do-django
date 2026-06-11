import datetime
from celery import current_app as celery_app
from celery.result import AsyncResult
from django.tasks.backends.base import BaseTaskBackend
from django.tasks import TaskResult, TaskResultStatus
from django.tasks.exceptions import TaskResultDoesNotExist
from .utils import store_task_mapping, get_task_from_result_id


class CeleryTaskBackend(BaseTaskBackend):
    supports_defer = True
    supports_get_result = True
    supports_priority = True
    supports_async_task = False

    def __init__(self, alias, params):
        super().__init__(alias=alias, params=params)
        self._default_queue = params.get("OPTIONS", {}).get("default_queue", "default")

    def enqueue(self, task, args, kwargs):
        full_task_name = f"{task.func.__module__}.{task.func.__name__}"

        celery_task = celery_app.task(
        task.func,
        name=full_task_name,
        queue=task.queue_name or self._default_queue,
        )
        eta = None
        countdown = None
        if task.run_after is not None:
            if isinstance(task.run_after, datetime.timedelta):
                countdown = task.run_after.total_seconds()
            else:
                eta = task.run_after
        async_result = celery_task.apply_async(
            args=args,
            kwargs=kwargs,
            eta=eta,
            countdown=countdown,
            priority=self._map_priority(task.priority),
            queue=task.queue_name or self._default_queue,
        )
        store_task_mapping(async_result.id, full_task_name)
        return self._build_task_result(
            task,
            async_result,
            args,
            kwargs,
        )

    def get_result(self, result_id):
        task = get_task_from_result_id(result_id)
        if task is None:
            raise TaskResultDoesNotExist(result_id)
        async_result = AsyncResult(result_id, app=celery_app)
        return self._build_task_result(task, async_result)

    def _build_task_result(self,task,async_result,args=(),kwargs=None,):
        status = self._map_celery_state(async_result.state)

        now = datetime.datetime.now(tz=datetime.timezone.utc)

        return TaskResult(
            task=task,
            id=async_result.id,
            status=status,

            enqueued_at=now,
            started_at=None,
            finished_at=None,

            last_attempted_at=now,

            args=(),
            kwargs={},

            errors=[],
            worker_ids=[],

            backend=self,
        )

    def _map_celery_state(self, celery_state):
        mapping = {
            "PENDING": TaskResultStatus.READY,
            "STARTED": TaskResultStatus.RUNNING,
            "RETRY": TaskResultStatus.READY,
            "SUCCESS": TaskResultStatus.SUCCESSFUL,
            "FAILURE": TaskResultStatus.FAILED,
            "REVOKED": TaskResultStatus.FAILED,
        }
        return mapping.get(celery_state, TaskResultStatus.READY)

    def _map_priority(self, django_priority):
        if django_priority is None:
            return 5
        normalized = (django_priority + 100) / 200
        return int((1 - normalized) * 9)
