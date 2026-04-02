from __future__ import annotations

import aiohttp
import feedparser

from trend_radar.collectors.base import BaseCollector
from trend_radar.config.schema import AppConfig, FeedConfig
from trend_radar.models import CollectorResult, TrendItem
from trend_radar.utils import compute_trend_score, detect_language, extract_hashtags, extract_keywords


class RSSGenericCollector(BaseCollector):
    name = "rss_generic"

    def is_available(self) -> bool:
        return True

    async def collect(self, config: AppConfig, session: aiohttp.ClientSession) -> CollectorResult:
        result = CollectorResult(name=self.name)
        collector_config = config.collectors.rss_generic
        items: list[TrendItem] = []
        for feed in collector_config.feeds:
            try:
                async with session.get(feed.url) as response:
                    response.raise_for_status()
                    content = await response.text()
                parsed = feedparser.parse(content)
                items.extend(self._parse_feed(feed=feed, payload=parsed.entries))
            except Exception as exc:  # pragma: no cover
                result.warnings.append(f"RSS feed {feed.name} skipped: {exc}")
        result.items = items[: collector_config.max_items]
        return result.finish()

    @staticmethod
    def _parse_feed(feed: FeedConfig, payload: list[dict]) -> list[TrendItem]:
        items: list[TrendItem] = []
        for entry in payload:
            title = str(entry.get("title", "")).strip()
            link = str(entry.get("link", "")).strip()
            if not title or not link:
                continue
            description = str(entry.get("summary", "") or entry.get("description", "")).strip()
            hashtags = extract_hashtags(title, description)
            keywords = extract_keywords(title=title, description=description, hashtags=hashtags)
            metrics = {"mentions": len(keywords), "feed": feed.name}
            items.append(
                TrendItem(
                    platform="rss_generic",
                    item_id=str(entry.get("id", link)),
                    title=title,
                    url=link,
                    author=str(entry.get("author", "")),
                    description=description,
                    metrics=metrics,
                    hashtags=hashtags,
                    keywords=keywords,
                    category=feed.name.lower().replace(" ", "-"),
                    language=detect_language(f"{title} {description}"),
                    trend_score=compute_trend_score(metrics),
                    source_type="article",
                )
            )
        return items
