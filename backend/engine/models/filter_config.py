"""Typed filter configuration replacing raw Dict."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FilterConfig:
    older_than_days: int = 180
    exclude_attachments: bool = True
    exclude_important: bool = True
    exclude_starred: bool = True
    min_size_mb: Optional[int] = None
    max_size_mb: Optional[int] = None
    sender_domains: List[str] = field(default_factory=list)
    sender_emails: List[str] = field(default_factory=list)
    exclude_senders: List[str] = field(default_factory=list)
    subject_keywords: List[str] = field(default_factory=list)
    exclude_labels: List[str] = field(default_factory=lambda: ["TRASH", "SPAM"])

    @classmethod
    def from_dict(cls, d: dict) -> "FilterConfig":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in known})

    def to_dict(self) -> dict:
        from dataclasses import asdict
        return asdict(self)
