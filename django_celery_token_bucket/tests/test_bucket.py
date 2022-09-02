from types import SimpleNamespace

import mock
from celery import schedules
from django.test import TestCase

from django_celery_token_bucket.bucket import TokenBucket


class TokenBucketTestCase(TestCase):
    @mock.patch("kombu.entity.Queue")
    def test_get_queue(self, mock_queue: mock.Mock):
        TokenBucket(
            name="my_custom_api",
            schedule=schedules.crontab(minute=0),
            amount=10,
            maximum=10,
        ).get_queue()

        mock_queue.assert_called_once_with(name="token_bucket_my_custom_api", max_length=10, durable=True)

    @mock.patch("django_celery_beat.models.CrontabSchedule")
    def test_get_or_create_schedule(self, mock_crontabschedule):
        """
        make sure the right schedule would be created
        """
        mock_crontabschedule_return_value = SimpleNamespace(id=None)
        mock_crontabschedule_return_value.save = mock.Mock()
        mock_crontabschedule.from_schedule = mock.Mock(return_value=mock_crontabschedule_return_value)

        test_schedule = schedules.crontab(minute=0)
        TokenBucket(
            name="my_custom_api",
            schedule=test_schedule,
            amount=10,
            maximum=10,
        )._get_or_create_schedule()

        mock_crontabschedule.from_schedule.assert_called_once_with(schedule=test_schedule)
        mock_crontabschedule_return_value.save.assert_called_once_with()

    @mock.patch("django_celery_beat.models.CrontabSchedule")
    @mock.patch("django_celery_beat.models.PeriodicTask")
    def test_create_periodic_task(self, mock_periodictask, mock_crontabschedule):
        """
        make sure the right period task would be created
        """
        mock_periodictask.objects.update_or_create = mock.Mock()

        token_bucket = TokenBucket(
            name="my_custom_api",
            schedule=schedules.crontab(),
            amount=10,
            maximum=10,
        )
        token_bucket_get_or_create_schedule_return_value = mock_crontabschedule()
        token_bucket._get_or_create_schedule = mock.Mock(return_value=token_bucket_get_or_create_schedule_return_value)

        token_bucket.create_periodic_task()

        mock_periodictask.objects.update_or_create.assert_called_once_with(
            name="token_bucket_refill_my_custom_api",
            defaults=dict(
                queue="celery",
                kwargs='{"name": "my_custom_api"}',
                task="django_celery_token_bucket.tasks.token_bucket_refill",
                interval=None,
                crontab=token_bucket_get_or_create_schedule_return_value,
            ),
        )
