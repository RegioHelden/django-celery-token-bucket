import logging
from typing import List

from django.conf import settings
from django.core.management import BaseCommand
from django_celery_beat.models import PeriodicTask

from django_celery_token_bucket.bucket import TokenBucket

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Register scheduled refill jobs for all token buckets'

    valid_bucket_names: List[str] = []

    def handle(self, *args, **options):
        token_bucket: TokenBucket
        for _, token_bucket in settings.CELERY_TOKEN_BUCKETS.items():
            # add a periodic task to our main queue to refill the tokens
            token_bucket.create_periodic_task()
            logging.info(
                f"created/updated periodic task to refill '{token_bucket.name}' with {token_bucket.amount} "
                f"new token(s) every {token_bucket.schedule}"
            )

            # mark bucket name as valid
            self.valid_bucket_names.append(token_bucket.name)

        # cleanup
        self.remove_outdated_periodic_tasks()
        self.remove_outdated_queues()

    def remove_outdated_periodic_tasks(self):
        for periodictask in PeriodicTask.objects.filter(name__startswith=TokenBucket.PERIODICTASK_PREFIX):
            # check if task is in allowed task name list
            name = periodictask.name.replace(TokenBucket.PERIODICTASK_PREFIX, "")
            if name in self.valid_bucket_names:
                continue

            # delete outdated task
            periodictask.delete()

    def remove_outdated_queues(self):
        # not implemented as there seems to be no way to list all (incl. inactive) queues
        return
