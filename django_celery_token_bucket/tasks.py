from celery import shared_task
from django.conf import settings
from kombu import Queue

from django_celery_token_bucket.bucket import TokenBucket


@shared_task
def token_bucket_token():
    return 1


@shared_task
def token_bucket_refill(name: str, *args, **kwargs):
    token_bucket: TokenBucket

    for token_bucket in settings.CELERY_TOKEN_BUCKETS:
        # get the right bucket
        if token_bucket.name != name:
            continue

        # prepare queue object
        queue = Queue(name=token_bucket.get_queue_name(), max_length=token_bucket.maximum)

        # fill it up
        for _ in range(token_bucket.amount):
            token_bucket_token.apply_async(queue=queue)
        return

    raise Exception(f"bucket '{name}' is not registered")
