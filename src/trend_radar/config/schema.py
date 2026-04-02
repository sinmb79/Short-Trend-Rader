from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BaseConfigModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class FeedConfig(BaseConfigModel):
    name: str
    url: str


class CollectorConfig(BaseConfigModel):
    enabled: bool = True
    max_items: int = 20


class YouTubeConfig(CollectorConfig):
    regions: list[str] = Field(default_factory=lambda: ["KR", "US"])
    categories: list[str] = Field(default_factory=lambda: ["trending", "shorts"])


class RedditConfig(CollectorConfig):
    subreddits: list[str] = Field(default_factory=lambda: ["popular", "technology", "videos"])
    sort: Literal["hot", "new", "rising"] = "hot"


class GoogleTrendsConfig(CollectorConfig):
    regions: list[str] = Field(default_factory=lambda: ["KR", "US"])


class RSSCollectorConfig(CollectorConfig):
    feeds: list[FeedConfig] = Field(default_factory=list)


class NaverDataLabConfig(CollectorConfig):
    client_id_env: str = "NAVER_CLIENT_ID"
    client_secret_env: str = "NAVER_CLIENT_SECRET"
    keyword_groups: list[str] = Field(default_factory=list)


class CollectorsConfig(BaseConfigModel):
    youtube: YouTubeConfig = Field(default_factory=YouTubeConfig)
    reddit: RedditConfig = Field(default_factory=RedditConfig)
    google_trends: GoogleTrendsConfig = Field(default_factory=GoogleTrendsConfig)
    rss_generic: RSSCollectorConfig = Field(default_factory=RSSCollectorConfig)
    naver_datalab: NaverDataLabConfig = Field(default_factory=NaverDataLabConfig)


class InterestsConfig(BaseConfigModel):
    keywords: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    exclude_keywords: list[str] = Field(default_factory=list)


class OutputAlertsConfig(BaseConfigModel):
    enabled: bool = True
    spike_threshold: float = 3.0
    keywords: list[str] = Field(default_factory=list)


class OutputConfig(BaseConfigModel):
    base_dir: str = "~/.22b/trends"
    formats: list[str] = Field(default_factory=lambda: ["md", "json"])
    digest: bool = True
    alerts: OutputAlertsConfig = Field(default_factory=OutputAlertsConfig)


class ScheduleIntervalsConfig(BaseConfigModel):
    tier1: str = "1h"
    tier2: str = "6h"
    tier3: str = "12h"


class ScheduleConfig(BaseConfigModel):
    mode: Literal["daemon", "cron", "once"] = "once"
    intervals: ScheduleIntervalsConfig = Field(default_factory=ScheduleIntervalsConfig)


class LimitsConfig(BaseConfigModel):
    max_storage_gb: int = 5
    cleanup_after_days: int = 30


class AppConfig(BaseConfigModel):
    collectors: CollectorsConfig = Field(default_factory=CollectorsConfig)
    interests: InterestsConfig = Field(default_factory=InterestsConfig)
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    limits: LimitsConfig = Field(default_factory=LimitsConfig)
