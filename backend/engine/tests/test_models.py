"""Tests for models/deletion_result.py."""

from datetime import datetime
from models.deletion_result import DeletionResult, BatchResult, PerformanceStats


def _make_result(**kwargs):
    defaults = {
        "deleted_count": 0,
        "error_count": 0,
        "duration_seconds": 1.0,
        "start_time": datetime.now(),
        "end_time": datetime.now(),
    }
    defaults.update(kwargs)
    return DeletionResult(**defaults)


# -- DeletionResult ----------------------------------------------------------


class TestDeletionResultTotalProcessed:
    def test_sums_deleted_and_errors(self):
        r = _make_result(deleted_count=10, error_count=3)
        assert r.total_processed == 13

    def test_zero_when_nothing_processed(self):
        r = _make_result(deleted_count=0, error_count=0)
        assert r.total_processed == 0

    def test_only_errors(self):
        r = _make_result(deleted_count=0, error_count=5)
        assert r.total_processed == 5


class TestDeletionResultSuccessRate:
    def test_partial_success(self):
        r = _make_result(deleted_count=9, error_count=1)
        assert r.success_rate == 90.0

    def test_full_success(self):
        r = _make_result(deleted_count=50, error_count=0)
        assert r.success_rate == 100.0

    def test_zero_success(self):
        r = _make_result(deleted_count=0, error_count=10)
        assert r.success_rate == 0.0

    def test_zero_division_returns_zero(self):
        r = _make_result(deleted_count=0, error_count=0)
        assert r.success_rate == 0.0


class TestDeletionResultDeletionRate:
    def test_normal_rate(self):
        r = _make_result(deleted_count=100, duration_seconds=10.0)
        assert r.deletion_rate == 10.0

    def test_fractional_rate(self):
        r = _make_result(deleted_count=1, duration_seconds=3.0)
        assert abs(r.deletion_rate - 1 / 3) < 1e-9

    def test_zero_duration_returns_zero(self):
        r = _make_result(deleted_count=100, duration_seconds=0.0)
        assert r.deletion_rate == 0.0

    def test_negative_duration_returns_zero(self):
        r = _make_result(deleted_count=100, duration_seconds=-1.0)
        assert r.deletion_rate == 0.0


# -- BatchResult --------------------------------------------------------------


class TestBatchResultRate:
    def test_includes_errors_in_rate(self):
        b = BatchResult(batch_number=1, deleted_count=40, error_count=20, duration_seconds=2.0)
        assert b.batch_rate == 30.0  # (40+20)/2

    def test_all_deleted_no_errors(self):
        b = BatchResult(batch_number=1, deleted_count=60, error_count=0, duration_seconds=2.0)
        assert b.batch_rate == 30.0

    def test_all_errors_no_deleted(self):
        b = BatchResult(batch_number=1, deleted_count=0, error_count=10, duration_seconds=5.0)
        assert b.batch_rate == 2.0

    def test_zero_duration_returns_zero(self):
        b = BatchResult(batch_number=1, deleted_count=60, error_count=0, duration_seconds=0.0)
        assert b.batch_rate == 0.0

    def test_negative_duration_returns_zero(self):
        b = BatchResult(batch_number=1, deleted_count=60, error_count=0, duration_seconds=-0.5)
        assert b.batch_rate == 0.0


# -- PerformanceStats ---------------------------------------------------------


class TestPerformanceStatsBatchApiEfficiency:
    def test_mixed_success_and_fallbacks(self):
        s = PerformanceStats(batch_api_success=8, batch_api_fallbacks=2)
        assert s.batch_api_efficiency == 80.0

    def test_all_success_no_fallbacks(self):
        s = PerformanceStats(batch_api_success=10, batch_api_fallbacks=0)
        assert s.batch_api_efficiency == 100.0

    def test_all_fallbacks_no_success(self):
        s = PerformanceStats(batch_api_success=0, batch_api_fallbacks=5)
        assert s.batch_api_efficiency == 0.0

    def test_zero_attempts_returns_zero(self):
        s = PerformanceStats()
        assert s.batch_api_efficiency == 0.0
