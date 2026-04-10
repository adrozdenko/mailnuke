"""Tests for services/deletion_orchestrator.py."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from services.deletion_orchestrator import DeletionOrchestrator
from models.filter_config import FilterConfig
from constants import DEFAULT_FILTERS, EMAILS_PER_TASK


@pytest.fixture
def mock_deps():
    """Patch all four orchestrator dependencies at their import paths."""
    with patch("services.deletion_orchestrator.GmailClient") as mc, \
         patch("services.deletion_orchestrator.EmailDeleter") as md, \
         patch("services.deletion_orchestrator.PerformanceTracker") as mp, \
         patch("services.deletion_orchestrator.QueryBuilder") as mq:

        # --- GmailClient ---
        gmail = mc.return_value
        gmail.get_service = AsyncMock()
        gmail.get_initial_email_count = AsyncMock(return_value=5)
        gmail.get_email_batch = AsyncMock(side_effect=[
            ["m1", "m2", "m3", "m4", "m5"],
            [],
        ])
        gmail.connection_reuse_count = 0

        # --- EmailDeleter ---
        deleter = md.return_value
        deleter.delete_email_batch = AsyncMock(return_value=(5, 0))
        deleter.rate_limit_counter = 0

        # --- PerformanceTracker ---
        tracker = mp.return_value
        tracker.start_tracking = MagicMock()
        tracker.stats = MagicMock(total_deleted=5, total_errors=0)
        tracker.get_current_rate = MagicMock(return_value=50.0)
        tracker.get_recent_average_rate = MagicMock(return_value=50.0)
        tracker.get_memory_usage_mb = MagicMock(return_value=30.0)
        tracker.record_batch_performance = MagicMock()
        tracker.should_print_periodic_status = MagicMock(return_value=False)
        tracker.perform_maintenance_if_needed = MagicMock()
        tracker.update_stats = MagicMock()
        tracker.get_final_results = MagicMock(return_value={
            "total_deleted": 5,
            "total_errors": 0,
            "duration_seconds": 1.0,
            "deletion_rate": 5.0,
            "success_rate": 100.0,
            "batch_api_efficiency": 100.0,
            "connection_reuses": 1,
            "rate_limit_hits": 0,
        })

        # --- QueryBuilder ---
        qb = mq.return_value
        qb.build_query = MagicMock(return_value="before:2026/01/01")

        yield {
            "gmail_client": gmail,
            "email_deleter": deleter,
            "perf_tracker": tracker,
            "query_builder": qb,
        }


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestInit:
    def test_accepts_dict_filters(self, mock_deps):
        """__init__ converts a raw dict into FilterConfig."""
        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        assert isinstance(orch.filters, FilterConfig)

    def test_accepts_filter_config(self, mock_deps):
        """__init__ passes through an existing FilterConfig."""
        cfg = FilterConfig(older_than_days=30)
        orch = DeletionOrchestrator(cfg)
        assert orch.filters is cfg
        assert orch.filters.older_than_days == 30


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------

class TestDryRun:
    async def test_returns_immediately_without_deleting(self, mock_deps):
        """dry_run=True should return early and never call delete."""
        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        result = await orch.execute_deletion(dry_run=True)

        assert result["dry_run"] is True
        assert result["total_deleted"] == 0
        assert result["estimated"] == 5
        mock_deps["email_deleter"].delete_email_batch.assert_not_called()

    async def test_dry_run_still_reports_estimated_count(self, mock_deps):
        """The estimated field should reflect the initial count query."""
        mock_deps["gmail_client"].get_initial_email_count = AsyncMock(return_value=42)
        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        result = await orch.execute_deletion(dry_run=True)

        assert result["estimated"] == 42

    async def test_dry_run_does_not_start_tracking(self, mock_deps):
        """Performance tracking should not be started during a dry run."""
        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        await orch.execute_deletion(dry_run=True)

        mock_deps["perf_tracker"].start_tracking.assert_not_called()


# ---------------------------------------------------------------------------
# Batch splitting
# ---------------------------------------------------------------------------

class TestCreateTaskBatches:
    def test_splits_into_correct_chunks(self, mock_deps):
        """_create_task_batches splits IDs into chunks of EMAILS_PER_TASK."""
        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        ids = list(range(10))
        batches = orch._create_task_batches(ids)

        # Every batch is at most EMAILS_PER_TASK
        for b in batches:
            assert len(b) <= EMAILS_PER_TASK

        # Flattened result preserves order and content
        flat = [x for b in batches for x in b]
        assert flat == ids

    def test_single_batch_when_under_limit(self, mock_deps):
        """When len(ids) <= EMAILS_PER_TASK, get exactly one batch."""
        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        ids = list(range(EMAILS_PER_TASK))
        batches = orch._create_task_batches(ids)

        assert len(batches) == 1
        assert batches[0] == ids

    def test_empty_input_returns_empty(self, mock_deps):
        """Empty input should return an empty list of batches."""
        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        batches = orch._create_task_batches([])
        assert batches == []

    def test_exact_multiple_produces_no_partial_batch(self, mock_deps):
        """When len(ids) is an exact multiple, no partial batch appears."""
        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        ids = list(range(EMAILS_PER_TASK * 3))
        batches = orch._create_task_batches(ids)

        assert len(batches) == 3
        assert all(len(b) == EMAILS_PER_TASK for b in batches)

    def test_remainder_goes_into_final_batch(self, mock_deps):
        """Extra items beyond last full batch land in a smaller final batch."""
        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        ids = list(range(EMAILS_PER_TASK + 7))
        batches = orch._create_task_batches(ids)

        assert len(batches) == 2
        assert len(batches[0]) == EMAILS_PER_TASK
        assert len(batches[1]) == 7


# ---------------------------------------------------------------------------
# Task result processing
# ---------------------------------------------------------------------------

class TestProcessTaskResults:
    def test_handles_exception_in_results(self, mock_deps):
        """Exceptions in the results list should be logged, not crash."""
        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        results = [
            (5, 0),
            Exception("boom"),
            (3, 1),
        ]
        # Should not raise
        orch._process_task_results(results)

    def test_updates_stats_for_successful_results(self, mock_deps):
        """Each non-exception result should call update_stats."""
        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        results = [(10, 0), (8, 2)]
        orch._process_task_results(results)

        tracker = mock_deps["perf_tracker"]
        assert tracker.update_stats.call_count == 2
        tracker.update_stats.assert_any_call(10, 0)
        tracker.update_stats.assert_any_call(8, 2)

    def test_skips_stats_for_exceptions(self, mock_deps):
        """Exceptions should not trigger update_stats."""
        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        results = [Exception("fail"), Exception("also fail")]
        orch._process_task_results(results)

        mock_deps["perf_tracker"].update_stats.assert_not_called()

    def test_mixed_results_counted_correctly(self, mock_deps):
        """Only non-exception results should count toward stats updates."""
        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        results = [(2, 0), Exception("x"), (3, 1), Exception("y"), (1, 0)]
        orch._process_task_results(results)

        assert mock_deps["perf_tracker"].update_stats.call_count == 3


# ---------------------------------------------------------------------------
# Full deletion loop
# ---------------------------------------------------------------------------

class TestDeletionLoop:
    async def test_loops_until_batch_is_empty(self, mock_deps):
        """execute_deletion should call get_email_batch until it returns []."""
        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        result = await orch.execute_deletion()

        assert result["total_deleted"] == 5
        # First call returns IDs, second call returns [] -> loop exits
        assert mock_deps["gmail_client"].get_email_batch.call_count == 2

    async def test_multiple_batches(self, mock_deps):
        """When the API returns IDs across several calls, all are processed."""
        mock_deps["gmail_client"].get_email_batch = AsyncMock(side_effect=[
            ["a", "b", "c"],
            ["d", "e"],
            [],
        ])
        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        result = await orch.execute_deletion()

        assert mock_deps["gmail_client"].get_email_batch.call_count == 3
        # delete_email_batch is called per-task-batch inside each main batch,
        # but at minimum it gets invoked for each main batch
        assert mock_deps["email_deleter"].delete_email_batch.call_count >= 2

    async def test_finalize_called_after_loop(self, mock_deps):
        """get_final_results should be called exactly once after the loop."""
        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        await orch.execute_deletion()

        mock_deps["perf_tracker"].get_final_results.assert_called_once()

    async def test_performance_tracking_starts(self, mock_deps):
        """start_tracking must be called when not in dry-run mode."""
        orch = DeletionOrchestrator(DEFAULT_FILTERS.copy())
        await orch.execute_deletion()

        mock_deps["perf_tracker"].start_tracking.assert_called_once()
