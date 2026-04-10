"""Integration test: full deletion pipeline with mocked Gmail API boundary."""

import pytest
from unittest.mock import patch, MagicMock

from services.deletion_orchestrator import DeletionOrchestrator
from constants import DEFAULT_FILTERS


async def test_full_deletion_pipeline():
    """
    End-to-end pipeline test.

    Mocks the Gmail service at the boundary (pickle.load, os.path.exists, build)
    and verifies that the orchestrator correctly drives the full flow:
      1. Queries initial count
      2. Fetches a batch of 5 messages
      3. Deletes them via batchModify
      4. Fetches again, gets empty -> stops
      5. Reports correct totals
    """
    # Arrange
    mock_service = MagicMock()

    # list().execute() is called multiple times:
    #   1st: initial count check (maxResults=1)
    #   2nd: first email batch -> 5 messages
    #   3rd: second email batch -> empty, loop ends
    list_execute_results = [
        {"resultSizeEstimate": 5},
        {"messages": [{"id": f"m{i}"} for i in range(5)]},
        {"messages": []},
    ]
    list_mock = MagicMock()
    list_mock.execute = MagicMock(side_effect=list_execute_results)
    mock_service.users.return_value.messages.return_value.list.return_value = list_mock

    # batchModify().execute() returns None (success, no body)
    batch_mock = MagicMock()
    batch_mock.execute = MagicMock(return_value=None)
    mock_service.users.return_value.messages.return_value.batchModify.return_value = batch_mock

    # Act — patch at the Gmail client boundary so everything above is real
    with patch("services.gmail_client.os.path.exists", return_value=True), \
         patch("builtins.open", MagicMock()), \
         patch("services.gmail_client.pickle.load", return_value=MagicMock()), \
         patch("services.gmail_client.build", return_value=mock_service):

        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        result = await orch.execute_deletion()

    # Assert
    assert result is not None, "Result should not be None"
    assert result["total_deleted"] == 5
    assert result["total_errors"] == 0
    assert result["duration_seconds"] > 0
    assert result["deletion_rate"] >= 0
    assert result["success_rate"] == 100.0
    assert "batch_api_efficiency" in result
    assert "connection_reuses" in result
