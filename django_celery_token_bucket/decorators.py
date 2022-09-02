from functools import wraps
from kombu.connection import Connection
from kombu.entity import Queue

from django.conf import settings

from django_celery_token_bucket.bucket import TokenBucket


def rate_limit(token_bucket_name: str, retry_backoff: int = 60, affect_task_retries: bool = False):
    def decorator_func(func):
        @wraps(func)
        def function(self, *args, **kwargs):
            try:
                token_bucket: TokenBucket = settings.CELERY_TOKEN_BUCKETS[token_bucket_name]
                token_queue: Queue = token_bucket.get_queue()
            except KeyError:
                raise Exception(f"bucket '{token_bucket_name}' is not registered")

            connection: Connection
            with self.app.connection_for_read() as connection:
                # bind queue to a channel of our connection
                token_queue.maybe_bind(channel=connection.default_channel)

                # try to get a message from the queue
                message = token_queue.get(no_ack=True)
                if message:
                    return func(self, *args, **kwargs)

                # decide if we need to increase the maximum retries
                max_retries = self.request.retries
                if not affect_task_retries:
                    max_retries += 1

                # no token left, retry with backoff
                raise self.retry(countdown=retry_backoff, max_retries=max_retries)

        return function

    return decorator_func
