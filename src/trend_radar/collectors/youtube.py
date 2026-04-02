from __future__ import annotations

import json
import re
from collections.abc import Iterable
from urllib.parse import urlencode

import aiohttp

from trend_radar.collectors.base import BaseCollector
from trend_radar.config.schema import AppConfig
from trend_radar.models import CollectorResult, TrendItem
from trend_radar.utils import (
    compute_trend_score,
    detect_language,
    extract_hashtags,
    extract_keywords,
    parse_compact_number,
)


YT_INITIAL_DATA_PATTERNS = [
    re.compile(r"var ytInitialData = (\{.*?\});", re.S),
    re.compile(r"window\[['\"]ytInitialData['\"]\]\s*=\s*(\{.*?\});", re.S),
]

CATEGORY_URLS = {
    "trending": "https://www.youtube.com/feed/trending",
    "music": "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D",
    "shorts": "https://www.youtube.com/results?search_query=viral+shorts",
}

REGION_LANG = {"KR": "ko", "US": "en"}


class YouTubeCollector(BaseCollector):
    name = "youtube"

    def is_available(self) -> bool:
        return True

    async def collect(self, config: AppConfig, session: aiohttp.ClientSession) -> CollectorResult:
        result = CollectorResult(name=self.name)
        collector_config = config.collectors.youtube
        items: dict[str, TrendItem] = {}
        for region in collector_config.regions:
            lang = REGION_LANG.get(region.upper(), "en")
            for category in collector_config.categories:
                url = self._build_url(region=region, category=category, lang=lang)
                try:
                    async with session.get(url, headers={"Accept-Language": f"{lang}-{region},en;q=0.8"}) as response:
                        response.raise_for_status()
                        html = await response.text()
                    for item in self._parse_listing(html=html, region=region, category=category):
                        items[item.item_id] = item
                except Exception as exc:  # pragma: no cover
                    result.warnings.append(f"YouTube {region}/{category} skipped: {exc}")
        result.items = list(items.values())[: collector_config.max_items]
        return result.finish()

    def _build_url(self, region: str, category: str, lang: str) -> str:
        base = CATEGORY_URLS.get(category, CATEGORY_URLS["trending"])
        separator = "&" if "?" in base else "?"
        return f"{base}{separator}{urlencode({'gl': region.upper(), 'hl': lang})}"

    @classmethod
    def _parse_listing(cls, html: str, region: str, category: str) -> list[TrendItem]:
        data = cls._extract_initial_data(html)
        renderers = cls._collect_renderers(data)
        items: list[TrendItem] = []
        for renderer in renderers:
            item = cls._renderer_to_item(renderer, region=region, category=category)
            if item:
                items.append(item)
        return items

    @classmethod
    def _extract_initial_data(cls, html: str) -> dict:
        for pattern in YT_INITIAL_DATA_PATTERNS:
            match = pattern.search(html)
            if match:
                return json.loads(match.group(1))
        raise ValueError("ytInitialData not found")

    @classmethod
    def _collect_renderers(cls, payload: object) -> list[dict]:
        found: list[dict] = []
        if isinstance(payload, dict):
            for key, value in payload.items():
                if key in {"videoRenderer", "gridVideoRenderer", "reelItemRenderer"} and isinstance(value, dict):
                    found.append({key: value})
                else:
                    found.extend(cls._collect_renderers(value))
        elif isinstance(payload, list):
            for item in payload:
                found.extend(cls._collect_renderers(item))
        return found

    @classmethod
    def _renderer_to_item(cls, wrapped_renderer: dict, region: str, category: str) -> TrendItem | None:
        renderer_type, renderer = next(iter(wrapped_renderer.items()))
        if renderer_type == "videoRenderer":
            item_id = renderer.get("videoId")
            title = cls._extract_text(renderer.get("title"))
            description = cls._extract_text(renderer.get("descriptionSnippet"))
            author = cls._extract_text(renderer.get("ownerText"))
            views = parse_compact_number(cls._extract_text(renderer.get("viewCountText")))
            url = f"https://www.youtube.com/watch?v={item_id}" if item_id else ""
            media_url = cls._extract_thumbnail(renderer.get("thumbnail"))
        elif renderer_type == "gridVideoRenderer":
            item_id = renderer.get("videoId")
            title = cls._extract_text(renderer.get("title"))
            description = ""
            author = cls._extract_text(renderer.get("shortBylineText"))
            views = parse_compact_number(cls._extract_text(renderer.get("viewCountText")))
            url = f"https://www.youtube.com/watch?v={item_id}" if item_id else ""
            media_url = cls._extract_thumbnail(renderer.get("thumbnail"))
        else:
            item_id = renderer.get("videoId")
            title = cls._extract_text(renderer.get("headline"))
            description = cls._extract_text(renderer.get("accessibility"))
            author = ""
            views = parse_compact_number(cls._extract_text(renderer.get("viewCountText")))
            url = f"https://www.youtube.com/shorts/{item_id}" if item_id else ""
            media_url = cls._extract_thumbnail(renderer.get("thumbnail"))
        if not item_id or not title or not url:
            return None
        hashtags = extract_hashtags(title, description)
        keywords = extract_keywords(title=title, description=description, hashtags=hashtags)
        metrics = {"views": views or 0, "region": region, "category": category}
        return TrendItem(
            platform="youtube",
            item_id=item_id,
            title=title,
            url=url,
            author=author,
            description=description,
            metrics=metrics,
            hashtags=hashtags,
            keywords=keywords,
            category=category,
            language=detect_language(f"{title} {description}"),
            trend_score=compute_trend_score(metrics),
            source_type="video",
            media_url=media_url,
        )

    @staticmethod
    def _extract_text(node: object) -> str:
        if not node:
            return ""
        if isinstance(node, dict):
            if "simpleText" in node:
                return str(node["simpleText"])
            if "runs" in node and isinstance(node["runs"], Iterable):
                return "".join(str(run.get("text", "")) for run in node["runs"] if isinstance(run, dict))
            if "accessibilityData" in node:
                return str(node["accessibilityData"].get("label", ""))
        return ""

    @staticmethod
    def _extract_thumbnail(node: object) -> str | None:
        if not isinstance(node, dict):
            return None
        thumbnails = node.get("thumbnails")
        if isinstance(thumbnails, list) and thumbnails:
            last = thumbnails[-1]
            if isinstance(last, dict):
                return str(last.get("url", "")) or None
        return None
