from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


@dataclass(slots=True)
class TrendItem:
    platform: str
    item_id: str
    title: str
    url: str
    author: str = ""
    description: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)
    hashtags: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    category: str = "general"
    language: str = "und"
    trend_score: float | None = None
    collected_at: str = field(default_factory=now_iso)
    source_type: str = "post"
    transcript: str | None = None
    media_url: str | None = None

    def __post_init__(self) -> None:
        self.hashtags = _unique_preserving_order(self.hashtags)
        self.keywords = _unique_preserving_order(self.keywords)

    def to_dict(self) -> dict[str, Any]:
        return {
            "platform": self.platform,
            "item_id": self.item_id,
            "title": self.title,
            "url": self.url,
            "author": self.author,
            "description": self.description,
            "metrics": self.metrics,
            "hashtags": self.hashtags,
            "keywords": self.keywords,
            "category": self.category,
            "language": self.language,
            "trend_score": self.trend_score,
            "collected_at": self.collected_at,
            "source_type": self.source_type,
            "transcript": self.transcript,
            "media_url": self.media_url,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TrendItem":
        return cls(**payload)


@dataclass(slots=True)
class CollectorResult:
    name: str
    items: list[TrendItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    skipped: bool = False
    started_at: str = field(default_factory=now_iso)
    finished_at: str | None = None

    def finish(self) -> "CollectorResult":
        self.finished_at = now_iso()
        return self


@dataclass(slots=True)
class RunReport:
    output_dir: str
    total_items: int
    collectors: dict[str, CollectorResult]
    index_path: str
    digest_path: str | None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _unique_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = value.strip()
        key = cleaned.casefold()
        if not cleaned or key in seen:
            continue
        seen.add(key)
        result.append(cleaned)
    return result
