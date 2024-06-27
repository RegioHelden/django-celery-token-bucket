# Changelog

## [3.0.0] - 2024-06-27

Contributors: [@lociii](https://github.com/lociii)

- Remove support for EOL `Django` versions `3.2`, `4.0` and `4.1`
- Add support for `Django` version `5.0`
- Minimum required `celery` version is now `5.3.0`, released 06/2023
- Minimum required `django-celery-beat` version is now `2.5.0`, releases 03/2023
- Minimum required `kombu` version is now `5.3.0`, releases 06/2023
- Renovate build environment

## [2.1.0] - 2023-01-03

Contributors: [@lociii](https://github.com/lociii)

### Changed

- The token holding job `token_bucket_token` will now ignore it's result and should not pop up in result backends stuck as pending anymore.
- Minimum required version of django-celery-beat is now 2.4.0 which adds support for Django 4.1

## [2.0.0] - 2022-09-02

Contributors: [@lociii](https://github.com/lociii)

### Changed

- Fix token consumption, see [#4](https://github.com/RegioHelden/django-celery-token-bucket/pull/4)

### Breaking

- Renamed `retry_backoff` to `countdown` to align wording with Celery and better reflect the behavior, see [#4](https://github.com/RegioHelden/django-celery-token-bucket/pull/4) and [docs](https://github.com/RegioHelden/django-celery-token-bucket#countdown)

## [1.1.0] - 2022-08-30

Contributors: [@Esquire-gh](https://github.com/Esquire-gh)

### Changed

- Make the refill queue name configurable per bucket, see [#2](https://github.com/RegioHelden/django-celery-token-bucket/pull/2) and [docs](https://github.com/RegioHelden/django-celery-token-bucket#token_refill_queue)
- Make it configurable if a failed token retrieval should increase the retry count, see [#2](https://github.com/RegioHelden/django-celery-token-bucket/pull/2) and [docs](https://github.com/RegioHelden/django-celery-token-bucket#affect_task_retries)

## [1.0]

Contributors: [@lociii](https://github.com/lociii), [@Esquire-gh](https://github.com/Esquire-gh)

- Initial release
