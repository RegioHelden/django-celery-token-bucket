import json
from dataclasses import dataclass
from typing import Optional

from celery import schedules
from django.conf import settings


@dataclass
class TokenBucket:
    """
    dataclass for holding details of a token bucket queue

    name: str -> the name of the queue (only letters and underscore)
    schedule: schedules.crontab -> how often tokens should be refilled
    amount: int -> the amount to refill for each schedule
    maximum: int -> the maximum amount of tokens the bucket can hold
    token_refill_queue: str -> optional name of the queue that our refill job will be executed in
    """

    name: str
    schedule: schedules.crontab
    amount: int
    maximum: int
    token_refill_queue: Optional[str] = None

    QUEUE_PREFIX: str = "token_bucket_"
    PERIODICTASK_PREFIX: str = "token_bucket_refill_"

    def get_queue(self):
        from kombu.entity import Queue
        return Queue(
            name=f"{self.QUEUE_PREFIX}{self.name}",
            max_length=self.maximum,
            durable=True,
        )

    def _get_or_create_schedule(self):
        from django_celery_beat.models import CrontabSchedule

        crontabschedule = CrontabSchedule.from_schedule(schedule=self.schedule)
        if not crontabschedule.id:
            crontabschedule.save()
        return crontabschedule

    def create_periodic_task(self):
        from django_celery_beat.models import PeriodicTask

        crontabschedule = self._get_or_create_schedule()

        if not self.token_refill_queue:
            try:
                self.token_refill_queue = settings.CELERY_DEFAULT_QUEUE
            except AttributeError:
                self.token_refill_queue = 'celery'

        PeriodicTask.objects.update_or_create(
            name=f"{self.PERIODICTASK_PREFIX}{self.name}",
            defaults=dict(
                queue=self.token_refill_queue,
                kwargs=json.dumps(dict(name=self.name)),
                task="django_celery_token_bucket.tasks.token_bucket_refill",
                interval=None,
                crontab=crontabschedule,
            ),
        )
