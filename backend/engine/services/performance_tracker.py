#!/usr/bin/env python3
"""Performance monitoring and tracking service"""

import time
import psutil
import gc
from datetime import datetime
from typing import List
from models.deletion_result import PerformanceStats
from constants import MAX_PERFORMANCE_SAMPLES, PERFORMANCE_CHECK_INTERVAL_SECONDS


class PerformanceTracker:
    """Monitors and tracks deletion performance"""
    
    def __init__(self):
        self.start_time = None
        self.performance_samples = []
        self.last_performance_check = time.time()
        self.process = psutil.Process()
        self.stats = PerformanceStats()
    
    def start_tracking(self):
        """Start performance tracking"""
        self.start_time = datetime.now()
        self.last_performance_check = time.time()
    
    def record_batch_performance(self, email_count: int, duration: float):
        """Record performance for a completed batch"""
        if duration <= 0:
            return
        
        rate = email_count / duration
        self.performance_samples.append(rate)
        self._maintain_sample_size()
    
    def _maintain_sample_size(self):
        """Keep performance samples within limit"""
        if len(self.performance_samples) > MAX_PERFORMANCE_SAMPLES:
            self.performance_samples.pop(0)
    
    def get_current_rate(self, total_deleted: int) -> float:
        """Get current overall deletion rate"""
        if not self.start_time:
            return 0.0
        
        total_time = time.time() - self.start_time.timestamp()
        return total_deleted / total_time if total_time > 0 else 0.0
    
    def get_recent_average_rate(self) -> float:
        """Get recent average rate from samples"""
        if not self.performance_samples:
            return 0.0
        return sum(self.performance_samples) / len(self.performance_samples)
    
    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        try:
            memory_info = self.process.memory_info()
            return memory_info.rss / 1024 / 1024
        except Exception:
            return 0.0
    
    def should_print_periodic_status(self) -> bool:
        """Check if it's time for periodic status update"""
        current_time = time.time()
        if current_time - self.last_performance_check > PERFORMANCE_CHECK_INTERVAL_SECONDS:
            self.last_performance_check = current_time
            return True
        return False
    
    def update_stats(self, deleted: int, errors: int):
        """Update performance statistics"""
        self.stats.total_deleted += deleted
        self.stats.total_errors += errors
    
    def increment_rate_limits(self):
        """Increment rate limit counter"""
        self.stats.rate_limit_hits += 1
    
    def increment_batch_api_success(self):
        """Increment successful batch API calls"""
        self.stats.batch_api_success += 1
    
    def increment_batch_api_fallback(self):
        """Increment batch API fallbacks"""
        self.stats.batch_api_fallbacks += 1
    
    def increment_connection_reuse(self):
        """Increment connection reuse counter"""
        self.stats.connection_reuses += 1
    
    def perform_maintenance_if_needed(self, batch_number: int):
        """Perform garbage collection maintenance"""
        from constants import MAINTENANCE_INTERVAL_BATCHES
        if batch_number % MAINTENANCE_INTERVAL_BATCHES == 0:
            gc.collect()
    
    def get_final_results(self) -> dict:
        """Get final performance results"""
        if not self.start_time:
            return {}
        
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        final_rate = self.stats.total_deleted / total_duration if total_duration > 0 else 0
        
        return {
            'total_deleted': self.stats.total_deleted,
            'total_errors': self.stats.total_errors,
            'duration_seconds': total_duration,
            'deletion_rate': final_rate,
            'success_rate': self._calculate_success_rate(),
            'batch_api_efficiency': self.stats.batch_api_efficiency,
            'connection_reuses': self.stats.connection_reuses,
            'rate_limit_hits': self.stats.rate_limit_hits
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate success rate percentage"""
        total = self.stats.total_deleted + self.stats.total_errors
        if total == 0:
            return 0.0
        return (self.stats.total_deleted / total) * 100