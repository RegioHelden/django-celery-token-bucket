from celery import shared_task
from django.conf import settings

from django_celery_token_bucket.bucket import TokenBucket


@shared_task(ignore_result=True)
def token_bucket_token():
    return 1


@shared_task
def token_bucket_refill(name: str, *args, **kwargs):
    token_bucket: TokenBucket

    # get queue
    try:
        token_bucket = settings.CELERY_TOKEN_BUCKETS[name]
    except KeyError as e:
        raise Exception(f"bucket '{name}' is not registered") from e
    queue = token_bucket.get_queue()

    # fill it up
    for _ in range(token_bucket.amount):
        token_bucket_token.apply_async(queue=queue)
