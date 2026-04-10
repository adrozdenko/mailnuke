"""Tests for services/gmail_client.py — mock only the filesystem/API boundary."""

import pytest
from unittest.mock import patch, MagicMock


def test_missing_token_pickle_raises_with_clear_message():
    with patch("services.gmail_client.os.path.exists", return_value=False):
        from services.gmail_client import GmailClient
        with pytest.raises(FileNotFoundError, match="token.pickle"):
            GmailClient()


def test_valid_credentials_loads_successfully():
    mock_creds = MagicMock()
    with patch("services.gmail_client.os.path.exists", return_value=True), \
         patch("builtins.open", MagicMock()), \
         patch("services.gmail_client.pickle.load", return_value=mock_creds), \
         patch("services.gmail_client.build"):
        from services.gmail_client import GmailClient
        client = GmailClient()
        assert client.credentials is mock_creds


@pytest.fixture
def client_and_service():
    mock_service = MagicMock()
    with patch("services.gmail_client.os.path.exists", return_value=True), \
         patch("builtins.open", MagicMock()), \
         patch("services.gmail_client.pickle.load", return_value=MagicMock()), \
         patch("services.gmail_client.build", return_value=mock_service):
        from services.gmail_client import GmailClient
        client = GmailClient()
        yield client, mock_service


async def test_get_service_reuses_connection_on_second_call(client_and_service):
    client, _ = client_and_service

    s1 = await client.get_service()
    s2 = await client.get_service()

    assert s1 is s2
    assert client.connection_reuse_count == 1


async def test_get_email_batch_returns_message_ids(client_and_service):
    client, service = client_and_service
    service.users().messages().list().execute.return_value = {
        "messages": [{"id": "a1"}, {"id": "b2"}, {"id": "c3"}]
    }

    ids = await client.get_email_batch("in:inbox", 10)

    assert ids == ["a1", "b2", "c3"]


async def test_get_email_batch_returns_empty_when_no_messages(client_and_service):
    client, service = client_and_service
    service.users().messages().list().execute.return_value = {"messages": []}

    ids = await client.get_email_batch("in:inbox", 10)

    assert ids == []


async def test_get_email_batch_returns_empty_on_api_error(client_and_service):
    client, service = client_and_service
    service.users().messages().list().execute.side_effect = Exception("API down")

    ids = await client.get_email_batch("in:inbox", 10)

    assert ids == []


async def test_get_initial_email_count_returns_estimate(client_and_service):
    client, service = client_and_service
    service.users().messages().list().execute.return_value = {
        "resultSizeEstimate": 42
    }

    count = await client.get_initial_email_count("category:promotions")

    assert count == 42


async def test_get_initial_email_count_returns_zero_on_error(client_and_service):
    client, service = client_and_service
    service.users().messages().list().execute.side_effect = Exception("fail")

    count = await client.get_initial_email_count("in:inbox")

    assert count == 0
