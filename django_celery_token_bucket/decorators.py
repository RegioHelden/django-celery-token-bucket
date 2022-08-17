from django.conf import settings
from functools import wraps
from queue import Empty
from bucket import TokenBucket


def rate_limit(token_bucket_name: str, retry_backoff: int = 60):
    def decorator_func(func):
        @wraps(func)
        def function(self, *args, **kwargs):
            with self.app.connection_for_read() as conn:
                queue_name = f"{TokenBucket.QUEUE_PREFIX}{token_bucket_name}"
                try:
                    token_bucket: TokenBucket = settings.CELERY_TOKEN_BUCKETS[token_bucket_name]
                except KeyError:
                    raise Exception(f"bucket '{token_bucket_name}' is not registered")

                with conn.SimpleQueue(queue_name, queue_opts={'max_length': token_bucket.maximum}) as queue:
                    try:
                        message = queue.get(block=True, timeout=5)
                        message.ack()
                        return func(self, *args, **kwargs)
                    except Empty:
                        self.retry(countdown=retry_backoff)

        return function

    return decorator_func
