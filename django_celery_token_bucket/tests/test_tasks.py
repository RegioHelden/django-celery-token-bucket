import mock

from django.test import TestCase

from django_celery_token_bucket import tasks


"""
all tests are based on CELERY_TOKEN_BUCKETS in settings.py of the docker module
"""

QUEUE_CONSTANT = 478362473


class TokenBucketTokenTaskTestCase(TestCase):
    def test_returns_one(self):
        """
        test that the message task just returns 1
        """
        self.assertEquals(1, tasks.token_bucket_token())


class TokenBucketRefillTaskTestCase(TestCase):
    @mock.patch("django_celery_token_bucket.bucket.TokenBucket.get_queue", return_value=QUEUE_CONSTANT)
    def test_not_called(self, mock_token_bucket_get_queue: mock.Mock):
        """
        make sure nothing happens when we try to refill a non-existing bucket
        """
        with self.assertRaisesMessage(Exception, "bucket 'does_not_exist' is not registered"):
            tasks.token_bucket_refill(name="does_not_exist")

        # make sure no queue has been set up
        mock_token_bucket_get_queue.assert_not_called()

    @mock.patch("django_celery_token_bucket.tasks.token_bucket_token.apply_async")
    @mock.patch("django_celery_token_bucket.bucket.TokenBucket.get_queue", return_value=QUEUE_CONSTANT)
    def test_called(self, mock_token_bucket_get_queue: mock.Mock, mock_token_bucket_token_apply_async: mock.Mock):
        """
        make sure that the right queue gets refilled with the right amount of tokens
        """
        tasks.token_bucket_refill(name="my_custom_api")

        # make sure the queue is set up correctly
        mock_token_bucket_get_queue.assert_called_once()

        # check that we have the right refill calls
        excpected_calls = []
        for _ in range(10):
            excpected_calls.append(mock.call(queue=QUEUE_CONSTANT))
        mock_token_bucket_token_apply_async.assert_has_calls(excpected_calls)
        self.assertEqual(10, mock_token_bucket_token_apply_async.call_count)
