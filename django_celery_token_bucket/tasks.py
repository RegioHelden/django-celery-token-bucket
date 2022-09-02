from celery import shared_task
from django.conf import settings
from kombu.entity import Queue

from django_celery_token_bucket.bucket import TokenBucket


@shared_task
def token_bucket_token():
    return 1


@shared_task
def token_bucket_refill(name: str, *args, **kwargs):
    token_bucket: TokenBucket

    # get queue
    try:
        token_bucket = settings.CELERY_TOKEN_BUCKETS[name]
    except KeyError:
        raise Exception(f"bucket '{name}' is not registered")
    queue = token_bucket.get_queue()

    # fill it up
    for _ in range(token_bucket.amount):
        token_bucket_token.apply_async(queue=queue)
    return
