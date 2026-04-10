"""Tests for services/performance_tracker.py — pure logic, mock only psutil."""

import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from services.performance_tracker import PerformanceTracker


# --- Rate calculations ---

def test_current_rate_with_elapsed_time():
    pt = PerformanceTracker()
    pt.start_time = datetime.now() - timedelta(seconds=2)

    rate = pt.get_current_rate(100)

    assert 45.0 < rate < 55.0  # ~50/sec, timing tolerance


def test_current_rate_returns_zero_before_start():
    pt = PerformanceTracker()

    assert pt.get_current_rate(100) == 0.0


def test_recent_average_rate_averages_samples():
    pt = PerformanceTracker()
    pt.record_batch_performance(100, 1.0)  # 100/s
    pt.record_batch_performance(200, 1.0)  # 200/s

    assert pt.get_recent_average_rate() == 150.0


def test_recent_average_rate_empty_returns_zero():
    pt = PerformanceTracker()

    assert pt.get_recent_average_rate() == 0.0


# --- Rolling window ---

def test_rolling_window_caps_at_10_samples():
    pt = PerformanceTracker()
    for _ in range(15):
        pt.record_batch_performance(100, 1.0)

    assert len(pt.performance_samples) == 10


def test_rolling_window_drops_oldest_first():
    pt = PerformanceTracker()
    for i in range(1, 13):
        pt.record_batch_performance(i * 10, 1.0)  # rates: 10,20,...,120

    # First two (10,20) dropped, oldest remaining is 30
    assert pt.performance_samples[0] == 30.0


def test_zero_duration_batch_is_skipped():
    pt = PerformanceTracker()
    pt.record_batch_performance(100, 0.0)

    assert len(pt.performance_samples) == 0


# --- Stats accumulation ---

def test_update_stats_accumulates():
    pt = PerformanceTracker()
    pt.update_stats(10, 2)
    pt.update_stats(5, 1)

    assert pt.stats.total_deleted == 15
    assert pt.stats.total_errors == 3


# --- Periodic status ---

def test_periodic_status_false_when_checked_recently():
    pt = PerformanceTracker()
    pt.last_performance_check = time.time()

    assert pt.should_print_periodic_status() is False


def test_periodic_status_true_after_30_seconds():
    pt = PerformanceTracker()
    pt.last_performance_check = time.time() - 60

    assert pt.should_print_periodic_status() is True


# --- Final results ---

def test_final_results_contains_all_keys():
    pt = PerformanceTracker()
    pt.start_tracking()
    pt.update_stats(50, 2)

    results = pt.get_final_results()

    assert results["total_deleted"] == 50
    assert results["total_errors"] == 2
    assert "duration_seconds" in results
    assert "deletion_rate" in results
    assert "success_rate" in results
    assert "batch_api_efficiency" in results
    assert "connection_reuses" in results


def test_final_results_empty_when_not_started():
    pt = PerformanceTracker()

    assert pt.get_final_results() == {}


def test_success_rate_zero_when_nothing_processed():
    pt = PerformanceTracker()

    assert pt._calculate_success_rate() == 0.0


def test_success_rate_calculation():
    pt = PerformanceTracker()
    pt.update_stats(90, 10)

    assert pt._calculate_success_rate() == 90.0
