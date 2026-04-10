"""Shared fixtures for gmail_bulk_delete test suite."""

import pytest
from unittest.mock import MagicMock, AsyncMock
from constants import DEFAULT_FILTERS


@pytest.fixture
def sample_filters():
    return DEFAULT_FILTERS.copy()


@pytest.fixture
def newsletter_filters():
    return {
        "older_than_days": 30,
        "exclude_attachments": True,
        "exclude_important": True,
        "exclude_starred": True,
        "min_size_mb": None,
        "max_size_mb": None,
        "sender_domains": ["mailchimp.com", "constantcontact.com"],
        "sender_emails": [],
        "exclude_senders": [],
        "subject_keywords": ["newsletter", "unsubscribe"],
        "exclude_labels": ["TRASH", "SPAM"],
    }


@pytest.fixture
def sample_message_ids():
    return [f"msg_{i}" for i in range(10)]


@pytest.fixture
def mock_gmail_service():
    """Mock Gmail API service with chainable methods."""
    service = MagicMock()

    # users().messages().list()
    list_mock = MagicMock()
    service.users.return_value.messages.return_value.list.return_value = list_mock

    # users().messages().batchModify()
    batch_mock = MagicMock()
    service.users.return_value.messages.return_value.batchModify.return_value = batch_mock

    # users().messages().trash()
    trash_mock = MagicMock()
    service.users.return_value.messages.return_value.trash.return_value = trash_mock

    return service


@pytest.fixture
def mock_gmail_client(mock_gmail_service):
    """Mock GmailClient that returns the mock service."""
    from unittest.mock import patch

    with patch("services.gmail_client.os.path.exists", return_value=True), \
         patch("services.gmail_client.pickle.load", return_value=MagicMock()), \
         patch("services.gmail_client.build", return_value=mock_gmail_service):
        from services.gmail_client import GmailClient
        client = GmailClient()
        client.service = mock_gmail_service
        yield client
