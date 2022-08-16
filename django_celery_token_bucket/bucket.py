import json
from dataclasses import dataclass

from celery import schedules


@dataclass
class TokenBucket:
    """
    dataclass for holding details of a token bucket Queue

    name: str -> the name of the queue (only letters and underscore)
    schedule: schedules.crontab -> how often tokens should be refilled
    amount: int -> the amount to refill for each schedule
    maximum: int -> the maximum amount of tokens the bucket can hold
    """

    name: str
    schedule: schedules.crontab
    amount: int
    maximum: int

    QUEUE_PREFIX: str = "token_bucket_"
    PERIODICTASK_PREFIX: str = "token_bucket_refill_"

    def get_queue_name(self):
        return f"{self.QUEUE_PREFIX}{self.name}"

    def _get_or_create_schedule(self):
        from django_celery_beat.models import CrontabSchedule

        crontabschedule = CrontabSchedule.from_schedule(schedule=self.schedule)
        if not crontabschedule.id:
            crontabschedule.save()
        return crontabschedule

    def create_periodic_task(self):
        from django_celery_beat.models import PeriodicTask

        crontabschedule = self._get_or_create_schedule()

        PeriodicTask.objects.update_or_create(
            name=f"{self.PERIODICTASK_PREFIX}{self.name}",
            defaults=dict(
                queue="token_bucket",
                kwargs=json.dumps(dict(name=self.name)),
                task="django_celery_token_bucket.tasks.token_bucket_refill",
                interval=None,
                crontab=crontabschedule,
            ),
        )
