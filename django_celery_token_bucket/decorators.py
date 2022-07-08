from functools import wraps
from queue import Empty


def rate_limit(token_bucket: str, retry_backoff: int = 60):
    def decorator_func(func):
        @wraps(func)
        def function(self, *args, **kwargs):
            with self.app.connection_for_read() as conn:
                with conn.SimpleQueue(token_bucket, no_ack=True) as queue:
                    try:
                        queue.get(block=True, timeout=5)
                        return func(self, *args, **kwargs)
                    except Empty:
                        self.retry(countdown=retry_backoff)

        return function

    return decorator_func
