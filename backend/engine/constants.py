#!/usr/bin/env python3
"""Configuration constants for Gmail bulk delete tool"""

# Email processing configuration
EMAILS_PER_CHUNK = 300
MAX_CONCURRENT_TASKS = 5
EMAILS_PER_TASK = 60

# Retry and timing configuration
MAX_RETRY_ATTEMPTS = 2
BACKOFF_BASE_DELAY = 0.05
STANDARD_DELAY = 0.05
ERROR_RECOVERY_DELAY = 0.5

# Maintenance and monitoring
MAINTENANCE_INTERVAL_BATCHES = 10
PERFORMANCE_CHECK_INTERVAL_SECONDS = 30
PROGRESS_BAR_WIDTH = 40

# Gmail API configuration
DATE_FORMAT = "%Y/%m/%d"
GMAIL_API_VERSION = 'v1'
USER_ID = 'me'

# Performance monitoring
MAX_PERFORMANCE_SAMPLES = 10
RATE_LIMIT_THRESHOLD = 5

# Default smart filtering configuration
DEFAULT_FILTERS = {
    "older_than_days": 180,
    "exclude_attachments": True,
    "exclude_important": True, 
    "exclude_starred": True,
    "min_size_mb": None,
    "max_size_mb": None,
    "sender_domains": [],
    "sender_emails": [],
    "exclude_senders": [],
    "subject_keywords": [],
    "exclude_labels": ["TRASH", "SPAM"]
}

# Predefined filter presets
FILTER_PRESETS = {
    "newsletters": {
        "older_than_days": 30,
        "exclude_attachments": True,
        "exclude_important": True,
        "exclude_starred": True,
        "subject_keywords": ["newsletter", "unsubscribe", "weekly digest", "monthly update"],
        "sender_domains": ["mailchimp.com", "constantcontact.com", "sendinblue.com"],
        "exclude_labels": ["TRASH", "SPAM"]
    },
    
    "github_notifications": {
        "older_than_days": 7,
        "exclude_attachments": True,
        "exclude_important": True,
        "exclude_starred": True,
        "sender_emails": ["notifications@github.com", "noreply@github.com"],
        "subject_keywords": ["[GitHub]", "Pull Request", "Issue"],
        "exclude_labels": ["TRASH", "SPAM"]
    },
    
    "large_emails": {
        "older_than_days": 90,
        "exclude_attachments": False,
        "exclude_important": True,
        "exclude_starred": True,
        "min_size_mb": 10,
        "exclude_labels": ["TRASH", "SPAM"]
    },
    
    "social_media": {
        "older_than_days": 14,
        "exclude_attachments": True,
        "exclude_important": True,
        "exclude_starred": True,
        "sender_domains": ["facebook.com", "twitter.com", "linkedin.com", "instagram.com"],
        "subject_keywords": ["notification", "activity", "friend request", "message"],
        "exclude_labels": ["TRASH", "SPAM"]
    },
    
    "promotional": {
        "older_than_days": 60,
        "exclude_attachments": True,
        "exclude_important": True,
        "exclude_starred": True,
        "subject_keywords": ["sale", "discount", "offer", "promo", "deal", "% off"],
        "exclude_labels": ["TRASH", "SPAM"]
    }
}