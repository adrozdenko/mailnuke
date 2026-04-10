"""Gmail query builder for smart filtering."""

from datetime import datetime, timedelta
from typing import List, Union
from constants import DATE_FORMAT
from models.filter_config import FilterConfig


class QueryBuilder:
    """Builds Gmail search queries from FilterConfig or raw dict."""

    def __init__(self, filters: Union[FilterConfig, dict]):
        if isinstance(filters, dict):
            self.filters = FilterConfig.from_dict(filters)
        else:
            self.filters = filters

    def build_query(self) -> str:
        parts = []
        parts.extend(self._date_filters())
        parts.extend(self._size_filters())
        parts.extend(self._sender_filters())
        parts.extend(self._subject_filters())
        parts.extend(self._exclusion_filters())
        return " ".join(parts)

    def _date_filters(self) -> List[str]:
        if not self.filters.older_than_days:
            return []
        cutoff = datetime.now() - timedelta(days=self.filters.older_than_days)
        return [f"before:{cutoff.strftime(DATE_FORMAT)}"]

    def _size_filters(self) -> List[str]:
        parts = []
        if self.filters.min_size_mb:
            parts.append(f"larger:{self.filters.min_size_mb}M")
        if self.filters.max_size_mb:
            parts.append(f"smaller:{self.filters.max_size_mb}M")
        return parts

    def _sender_filters(self) -> List[str]:
        parts = []
        parts.extend(self._or_group(
            [f"from:@{d}" for d in self.filters.sender_domains]
        ))
        parts.extend(self._or_group(
            [f"from:{e}" for e in self.filters.sender_emails]
        ))
        return parts

    def _subject_filters(self) -> List[str]:
        queries = [f'subject:"{kw}"' for kw in self.filters.subject_keywords]
        return self._or_group(queries)

    def _or_group(self, queries: List[str]) -> List[str]:
        if not queries:
            return []
        if len(queries) == 1:
            return queries
        return [f'({" OR ".join(queries)})']

    def _exclusion_filters(self) -> List[str]:
        parts = []
        if self.filters.exclude_attachments:
            parts.append("-has:attachment")
        if self.filters.exclude_important:
            parts.append("-is:important")
        if self.filters.exclude_starred:
            parts.append("-is:starred")
        for sender in self.filters.exclude_senders:
            parts.append(f"-from:{sender}")
        for label in self.filters.exclude_labels:
            parts.append(f"-in:{label.lower()}")
        return parts
