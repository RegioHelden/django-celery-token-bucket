# Django celery token bucket

A dynamic [token bucket](https://medium.com/analytics-vidhya/celery-throttling-setting-rate-limit-for-queues-5b5bf16c73ce) implementation using the database scheduler [django celery beat](https://github.com/celery/django-celery-beat).

## How it works

The bucket is represented by a celery queue that will not be processed by a worker but just hold our tokens (messages).
Whenever a rate limited task should be run, the decorator tries to consume a message from that queue. If the queue is empty, the task gets retried after the defined timeout.  
A periodic task will then refill the bucket with tokens whenever they should be available again.

## Define a token bucket

Buckets are defined in the Django config.

Following example allows one thousand tokens per hour to throttle access to a rate limited third party API.

Add to `settings.py` of your project.

```python
from typing import Dict
from celery import schedules
from django_celery_token_bucket import TokenBucket

INSTALLED_APPS = [
    ...,
    'django_celery_token_bucket'
]

CELERY_TOKEN_BUCKETS: Dict[str, TokenBucket] = {
    "my_api_client": TokenBucket(
        name="my_api_client",
        schedule=schedules.crontab(minute=0),  # once every hour
        amount=1000,
        maximum=1000,
    )
}
```

### name

The name must only consist of letters, numbers and the underscore character as it's used in the name of the celery
queue. It should also be the same as the key in the CELERY_TOKEN_BUCKETS dictionary.

### schedule

A `celery.schedules.crontab` that defines when the tokens should be refilled.

### amount

The amount of tokens to add whenever the scheduled refill is run.

### maximum

The maximum amount of tokens our bucket can hold.

## Sync period tasks to refill the buckets

A management command `token_bucket_register_periodic_tasks` is provided that should be run during deployment of your
application to sync the period tasks and make sure that buckets get properly refilled.

## Use the rate_limit decorator

The decorator will make sure that the task that gets decorated will not exceed the limit of available tokens.

```python
from my_app.celery import celery_app
from django_celery_token_bucket.decorators import rate_limit


@celery_app.task
@rate_limit(token_bucket="my_api_client", retry_backoff=300)
def my_tasK(*args, **kwargs):
    return
```

The above task will try to consume a token from the `my_api_client` and retries after 300 seconds if no token is
available.

## Run the tests locally

A docker-compose environment is provided to easily run the tests:

```bash
docker-compose run --rm django test
```

## Making a new release

[bumpversion](https://github.com/peritus/bumpversion) is used to manage releases.

Add your changes to the [CHANGELOG](./CHANGELOG.md), run

```bash
bumpversion <major|minor|patch>
```

and push (including tags).
