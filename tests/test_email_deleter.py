"""Tests for services/email_deleter.py."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from googleapiclient.errors import HttpError
from services.email_deleter import EmailDeleter
from constants import BACKOFF_BASE_DELAY, MAX_RETRY_ATTEMPTS


@pytest.fixture
def mock_client(mock_gmail_service):
    client = MagicMock()
    client.get_service = AsyncMock(return_value=mock_gmail_service)
    return client


@pytest.fixture
def deleter(mock_client):
    return EmailDeleter(mock_client)


def _make_http_error(status: int, message: bytes = b"error") -> HttpError:
    resp = MagicMock(status=status)
    return HttpError(resp, message)


class TestBatchDeleteSuccess:
    """Batch API succeeds on first try."""

    async def test_batch_success_returns_count_and_zero_errors(
        self, deleter, mock_gmail_service
    ):
        # Arrange
        mock_gmail_service.users().messages().batchModify().execute.return_value = None
        ids = ["m1", "m2", "m3"]

        # Act
        deleted, errors = await deleter.delete_email_batch(ids)

        # Assert
        assert deleted == 3
        assert errors == 0

    async def test_batch_success_does_not_call_individual_delete(
        self, deleter, mock_gmail_service
    ):
        # Arrange
        mock_gmail_service.users().messages().batchModify().execute.return_value = None

        # Act
        await deleter.delete_email_batch(["m1"])

        # Assert — trash() should never be reached
        mock_gmail_service.users().messages().trash().execute.assert_not_called()


class TestBatchFailsFallsBackToIndividual:
    """Batch API fails with non-rate-limit error, so we fall back to individual deletion."""

    async def test_individual_succeeds_after_batch_failure(
        self, deleter, mock_gmail_service
    ):
        # Arrange — batch raises 500, individual works
        mock_gmail_service.users().messages().batchModify().execute.side_effect = (
            _make_http_error(500, b"Internal error")
        )
        mock_gmail_service.users().messages().trash().execute.return_value = None

        # Act
        deleted, errors = await deleter.delete_email_batch(["m1", "m2"])

        # Assert
        assert deleted == 2
        assert errors == 0

    async def test_individual_partial_failure(self, deleter, mock_gmail_service):
        # Arrange — batch fails, individual fails for some
        mock_gmail_service.users().messages().batchModify().execute.side_effect = (
            _make_http_error(400, b"Bad request")
        )
        trash_exec = mock_gmail_service.users().messages().trash().execute
        trash_exec.side_effect = [
            None,  # m1 succeeds
            _make_http_error(404, b"Not found"),  # m2 fails
            None,  # m3 succeeds
        ]

        # Act
        deleted, errors = await deleter.delete_email_batch(["m1", "m2", "m3"])

        # Assert
        assert deleted == 2
        assert errors == 1


class TestRateLimitBehavior:
    """429/403 errors trigger counter increment and backoff, then fall through."""

    @patch("services.email_deleter.asyncio.sleep", new_callable=AsyncMock)
    async def test_429_increments_rate_limit_counter(
        self, mock_sleep, deleter, mock_gmail_service
    ):
        # Arrange — batch always hits 429, individual also 429
        mock_gmail_service.users().messages().batchModify().execute.side_effect = (
            _make_http_error(429, b"Rate limit exceeded")
        )
        mock_gmail_service.users().messages().trash().execute.side_effect = (
            _make_http_error(429, b"Rate limit exceeded")
        )

        # Act
        deleted, errors = await deleter.delete_email_batch(["m1"])

        # Assert
        assert deleted == 0
        assert errors == 1
        assert deleter.rate_limit_counter > 0

    @patch("services.email_deleter.asyncio.sleep", new_callable=AsyncMock)
    async def test_403_triggers_rate_limit_path(
        self, mock_sleep, deleter, mock_gmail_service
    ):
        # Arrange — batch always hits 403
        mock_gmail_service.users().messages().batchModify().execute.side_effect = (
            _make_http_error(403, b"Forbidden")
        )
        mock_gmail_service.users().messages().trash().execute.return_value = None

        # Act
        deleted, errors = await deleter.delete_email_batch(["m1"])

        # Assert — rate limit counter was bumped during batch retries
        assert deleter.rate_limit_counter > 0
        # Eventually fell back to individual which succeeded
        assert deleted == 1
        assert errors == 0

    @patch("services.email_deleter.asyncio.sleep", new_callable=AsyncMock)
    async def test_429_triggers_backoff_sleep(
        self, mock_sleep, deleter, mock_gmail_service
    ):
        # Arrange — batch hits 429 on every attempt (MAX_RETRY_ATTEMPTS times)
        mock_gmail_service.users().messages().batchModify().execute.side_effect = (
            _make_http_error(429, b"Rate limit exceeded")
        )
        mock_gmail_service.users().messages().trash().execute.return_value = None

        # Act
        await deleter.delete_email_batch(["m1"])

        # Assert — sleep was called at least once for backoff during batch retries
        # (MAX_RETRY_ATTEMPTS=2 means 1 retry with sleep before giving up)
        assert mock_sleep.await_count >= 1


class TestNonRateLimitError:
    """Non-429/403 HttpError returns False immediately, no retry."""

    async def test_batch_400_does_not_retry(self, deleter, mock_gmail_service):
        # Arrange
        batch_exec = mock_gmail_service.users().messages().batchModify().execute
        batch_exec.side_effect = _make_http_error(400, b"Bad request")
        mock_gmail_service.users().messages().trash().execute.return_value = None

        # Act
        await deleter.delete_email_batch(["m1"])

        # Assert — batchModify().execute() called only once (no retry)
        assert batch_exec.call_count == 1

    async def test_individual_404_no_retry(self, deleter, mock_gmail_service):
        # Arrange — batch fails so we fall back
        mock_gmail_service.users().messages().batchModify().execute.side_effect = (
            _make_http_error(500, b"Internal error")
        )
        trash_exec = mock_gmail_service.users().messages().trash().execute
        trash_exec.side_effect = _make_http_error(404, b"Not found")

        # Act
        deleted, errors = await deleter.delete_email_batch(["m1"])

        # Assert
        assert deleted == 0
        assert errors == 1
        # trash().execute() called only once per message (no retry on 404)
        assert trash_exec.call_count == 1


class TestBackoffCalculation:
    """_calculate_backoff_delay uses attempt, rate_limit_counter, and caps at 5."""

    def test_basic_calculation(self, deleter):
        # Arrange
        deleter.rate_limit_counter = 3

        # Act
        delay = deleter._calculate_backoff_delay(0)

        # Assert — BACKOFF_BASE_DELAY * (0+1) * min(3, 5)
        assert delay == BACKOFF_BASE_DELAY * 1 * 3

    def test_higher_attempt_scales_linearly(self, deleter):
        # Arrange
        deleter.rate_limit_counter = 2

        # Act
        delay = deleter._calculate_backoff_delay(4)

        # Assert — BACKOFF_BASE_DELAY * (4+1) * min(2, 5)
        assert delay == BACKOFF_BASE_DELAY * 5 * 2

    def test_rate_limit_counter_capped_at_5(self, deleter):
        # Arrange
        deleter.rate_limit_counter = 100

        # Act
        delay = deleter._calculate_backoff_delay(1)

        # Assert — BACKOFF_BASE_DELAY * (1+1) * min(100, 5) = capped at 5
        assert delay == BACKOFF_BASE_DELAY * 2 * 5

    def test_zero_counter_yields_zero_delay(self, deleter):
        # Arrange
        deleter.rate_limit_counter = 0

        # Act
        delay = deleter._calculate_backoff_delay(0)

        # Assert
        assert delay == 0.0


class TestRateLimitDetection:
    """_is_rate_limit_error checks for 429 or 403 in the error string."""

    def test_detects_429(self, deleter):
        err = _make_http_error(429, b"Rate limit")
        assert deleter._is_rate_limit_error(err) is True

    def test_detects_403(self, deleter):
        err = _make_http_error(403, b"Forbidden")
        assert deleter._is_rate_limit_error(err) is True

    def test_400_is_not_rate_limit(self, deleter):
        err = _make_http_error(400, b"Bad request")
        assert deleter._is_rate_limit_error(err) is False

    def test_500_is_not_rate_limit(self, deleter):
        err = _make_http_error(500, b"Internal server error")
        assert deleter._is_rate_limit_error(err) is False
