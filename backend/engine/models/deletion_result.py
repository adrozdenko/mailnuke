#!/usr/bin/env python3
"""Data models for deletion results"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DeletionResult:
    """Result of email deletion operation"""
    deleted_count: int
    error_count: int
    duration_seconds: float
    start_time: datetime
    end_time: datetime
    
    @property
    def total_processed(self) -> int:
        """Total emails processed"""
        return self.deleted_count + self.error_count
    
    @property
    def success_rate(self) -> float:
        """Success rate as percentage"""
        if self.total_processed == 0:
            return 0.0
        return (self.deleted_count / self.total_processed) * 100
    
    @property
    def deletion_rate(self) -> float:
        """Emails deleted per second"""
        if self.duration_seconds <= 0:
            return 0.0
        return self.deleted_count / self.duration_seconds


@dataclass
class BatchResult:
    """Result of single batch deletion"""
    batch_number: int
    deleted_count: int
    error_count: int
    duration_seconds: float
    
    @property
    def batch_rate(self) -> float:
        """Batch processing rate"""
        if self.duration_seconds <= 0:
            return 0.0
        return (self.deleted_count + self.error_count) / self.duration_seconds


@dataclass
class PerformanceStats:
    """Performance monitoring statistics"""
    total_deleted: int = 0
    total_errors: int = 0
    rate_limit_hits: int = 0
    batch_api_success: int = 0
    batch_api_fallbacks: int = 0
    connection_reuses: int = 0
    
    @property
    def batch_api_efficiency(self) -> float:
        """Batch API efficiency percentage"""
        total_attempts = self.batch_api_success + self.batch_api_fallbacks
        if total_attempts == 0:
            return 0.0
        return (self.batch_api_success / total_attempts) * 100