from functools import wraps

from django.conf import settings
from kombu.connection import Connection
from kombu.entity import Queue

from django_celery_token_bucket.bucket import TokenBucket


def rate_limit(token_bucket_name: str | list[str], countdown: int = 60, affect_task_retries: bool = False, weight: int = 1):
    def decorator_func(func):
        @wraps(func)
        def function(self, *args, **kwargs):
            if type(token_bucket_name) == str:
                self.token_bucket_name = [token_bucket_name, ]

            connection: Connection
            with self.app.connection_for_read() as connection:

                for name in token_bucket_name:
                    try:
                        token_bucket: TokenBucket = settings.CELERY_TOKEN_BUCKETS[name]
                        token_queue: Queue = token_bucket.get_queue()
                    except KeyError:
                        raise Exception(f"bucket '{name}' is not registered")

                    # bind queue to a channel of our connection
                    token_queue.maybe_bind(channel=connection.default_channel)

                    # try to get a message from the queue
                    message = token_queue.get(no_ack=True)
                    if message:
                        return func(self, *args, **kwargs)

                    # eventually reduce retry count
                    if not affect_task_retries:
                        self.request.retries = self.request.retries - weight

                    # no token left, retry after countdown
                    raise self.retry(countdown=countdown)

        return function

    return decorator_func
