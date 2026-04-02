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

    def to_dict(self, include_items: bool = False) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "item_count": len(self.items),
            "warnings": self.warnings,
            "errors": self.errors,
            "skipped": self.skipped,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }
        if include_items:
            payload["items"] = [item.to_dict() for item in self.items]
        return payload


@dataclass(slots=True)
class RunReport:
    output_dir: str
    total_items: int
    collectors: dict[str, CollectorResult]
    index_path: str
    digest_path: str | None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": "ok" if not self.errors else "warn",
            "output_dir": self.output_dir,
            "total_items": self.total_items,
            "index_path": self.index_path,
            "digest_path": self.digest_path,
            "warnings": self.warnings,
            "errors": self.errors,
            "collectors": {
                name: result.to_dict()
                for name, result in sorted(self.collectors.items())
            },
        }


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
