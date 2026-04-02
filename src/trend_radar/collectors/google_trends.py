from __future__ import annotations

import asyncio
from collections.abc import Iterable

import aiohttp
import feedparser

from trend_radar.collectors.base import BaseCollector
from trend_radar.config.schema import AppConfig
from trend_radar.models import CollectorResult, TrendItem
from trend_radar.utils import detect_language, parse_compact_number


PN_MAP = {
    "US": "united_states",
    "KR": "south_korea",
    "JP": "japan",
    "GB": "united_kingdom",
}


class GoogleTrendsCollector(BaseCollector):
    name = "google_trends"
    rss_endpoint = "https://trends.google.com/trending/rss?geo={region}"

    def is_available(self) -> bool:
        return True

    async def collect(self, config: AppConfig, session: aiohttp.ClientSession) -> CollectorResult:
        result = CollectorResult(name=self.name)
        collector_config = config.collectors.google_trends
        items: list[TrendItem] = []
        for region in collector_config.regions:
            try:
                async with session.get(self.rss_endpoint.format(region=region.upper())) as response:
                    response.raise_for_status()
                    content = await response.text()
                parsed = feedparser.parse(content)
                region_items = self._parse_feed(region=region, entries=parsed.entries[: collector_config.max_items])
                if region_items:
                    items.extend(region_items)
                    continue
            except Exception as exc:  # pragma: no cover
                result.warnings.append(f"Google Trends RSS {region} skipped: {exc}")

            try:
                fallback_items = await asyncio.to_thread(self._collect_sync, [region], collector_config.max_items)
                if fallback_items:
                    items.extend(fallback_items)
                else:
                    result.warnings.append(f"Google Trends {region} returned no items.")
            except Exception as exc:  # pragma: no cover
                result.warnings.append(f"Google Trends {region} skipped: {exc}")
        result.items = items
        return result.finish()

    @classmethod
    def _collect_sync(cls, regions: list[str], max_items: int) -> list[TrendItem]:
        from pytrends.request import TrendReq

        client = TrendReq(hl="en-US", tz=540)
        items: list[TrendItem] = []
        for region in regions:
            pn = PN_MAP.get(region.upper(), region.lower())
            frame = None
            if hasattr(client, "trending_searches"):
                try:
                    frame = client.trending_searches(pn=pn)
                except Exception:
                    frame = None
            if frame is None and hasattr(client, "daily_trending_searches"):
                frame = client.daily_trending_searches(pn=pn)
            terms = cls._extract_terms(frame)
            items.extend(cls._build_items(region=region, terms=terms[:max_items]))
        return items

    @staticmethod
    def _extract_terms(frame: object) -> list[str]:
        if frame is None:
            return []
        if hasattr(frame, "iloc"):
            first_column = frame.iloc[:, 0]
            return [str(value).strip() for value in first_column.tolist() if str(value).strip()]
        if isinstance(frame, Iterable):
            return [str(value).strip() for value in frame if str(value).strip()]
        return []

    @staticmethod
    def _parse_feed(region: str, entries: list[dict]) -> list[TrendItem]:
        items: list[TrendItem] = []
        for index, entry in enumerate(entries, start=1):
            title = str(entry.get("title", "")).strip()
            if not title:
                continue
            approx_traffic = parse_compact_number(str(entry.get("ht_approx_traffic", "")).replace("+", ""))
            items.append(
                TrendItem(
                    platform="google_trends",
                    item_id=f"{region.lower()}-{index}-{title.casefold().replace(' ', '-')}",
                    title=title,
                    url=str(entry.get("link", f"https://trends.google.com/trending/rss?geo={region.upper()}")),
                    description=str(entry.get("ht_news_item_title", "") or entry.get("summary", "")).strip(),
                    metrics={
                        "rank": index,
                        "region": region,
                        "approx_traffic": approx_traffic or 0,
                    },
                    keywords=[title],
                    category="search",
                    language=detect_language(title),
                    trend_score=round(max(10.0, min(100.0, (approx_traffic or 100) / 20.0)), 2),
                    source_type="search_term",
                    media_url=str(entry.get("ht_picture", "")) or None,
                )
            )
        return items

    @staticmethod
    def _build_items(region: str, terms: list[str]) -> list[TrendItem]:
        items: list[TrendItem] = []
        total = max(len(terms), 1)
        for index, term in enumerate(terms, start=1):
            score = round(max(10.0, 100.0 - ((index - 1) * (80.0 / total))), 2)
            items.append(
                TrendItem(
                    platform="google_trends",
                    item_id=f"{region.lower()}-{index}-{term.casefold().replace(' ', '-')}",
                    title=term,
                    url=f"https://trends.google.com/trends/trendingsearches/daily?geo={region.upper()}",
                    description=f"Google daily trending search in {region.upper()}",
                    metrics={"rank": index, "region": region},
                    keywords=[term],
                    category="search",
                    language=detect_language(term),
                    trend_score=score,
                    source_type="search_term",
                )
            )
        return items
