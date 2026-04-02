from __future__ import annotations

import aiohttp

from trend_radar.collectors.base import BaseCollector
from trend_radar.config.schema import AppConfig
from trend_radar.models import CollectorResult, TrendItem
from trend_radar.utils import compute_trend_score, detect_language, extract_hashtags, extract_keywords


class RedditCollector(BaseCollector):
    name = "reddit"

    def is_available(self) -> bool:
        return True

    async def collect(self, config: AppConfig, session: aiohttp.ClientSession) -> CollectorResult:
        result = CollectorResult(name=self.name)
        collector_config = config.collectors.reddit
        items: list[TrendItem] = []
        for subreddit in collector_config.subreddits:
            endpoint = f"https://www.reddit.com/r/{subreddit}/{collector_config.sort}.json?limit={collector_config.max_items}"
            try:
                async with session.get(endpoint, headers={"User-Agent": "trend-radar/0.1"}) as response:
                    response.raise_for_status()
                    payload = await response.json()
                items.extend(self._parse_listing(subreddit=subreddit, payload=payload))
            except Exception as exc:  # pragma: no cover
                result.warnings.append(f"Reddit r/{subreddit} skipped: {exc}")
        result.items = items[: collector_config.max_items]
        return result.finish()

    @staticmethod
    def _parse_listing(subreddit: str, payload: dict) -> list[TrendItem]:
        items: list[TrendItem] = []
        children = payload.get("data", {}).get("children", [])
        for child in children:
            data = child.get("data", {})
            title = data.get("title", "").strip()
            permalink = data.get("permalink", "")
            if not title or not permalink:
                continue
            description = data.get("selftext", "") or data.get("url_overridden_by_dest", "") or ""
            hashtags = extract_hashtags(title, description)
            keywords = extract_keywords(title=title, description=description, hashtags=hashtags)
            metrics = {
                "ups": data.get("ups", 0),
                "comments": data.get("num_comments", 0),
                "score": data.get("score", 0),
                "subreddit_subscribers": data.get("subreddit_subscribers", 0),
            }
            items.append(
                TrendItem(
                    platform="reddit",
                    item_id=data.get("id", permalink),
                    title=title,
                    url=f"https://www.reddit.com{permalink}",
                    author=data.get("author", ""),
                    description=description,
                    metrics=metrics,
                    hashtags=hashtags,
                    keywords=keywords,
                    category=subreddit.lower(),
                    language=detect_language(f"{title} {description}"),
                    trend_score=compute_trend_score(metrics),
                    source_type="post",
                )
            )
        return items
