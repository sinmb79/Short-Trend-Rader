from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from trend_radar.config.schema import AppConfig


@dataclass(slots=True)
class ScheduleDefinition:
    tier1: timedelta
    tier2: timedelta
    tier3: timedelta
    mode: str


def parse_interval(value: str) -> timedelta:
    cleaned = value.strip().lower()
    if cleaned.endswith("h"):
        return timedelta(hours=int(cleaned[:-1]))
    if cleaned.endswith("m"):
        return timedelta(minutes=int(cleaned[:-1]))
    if cleaned.endswith("d"):
        return timedelta(days=int(cleaned[:-1]))
    raise ValueError(f"Unsupported interval format: {value}")


def build_schedule(config: AppConfig) -> ScheduleDefinition:
    return ScheduleDefinition(
        tier1=parse_interval(config.schedule.intervals.tier1),
        tier2=parse_interval(config.schedule.intervals.tier2),
        tier3=parse_interval(config.schedule.intervals.tier3),
        mode=config.schedule.mode,
    )
