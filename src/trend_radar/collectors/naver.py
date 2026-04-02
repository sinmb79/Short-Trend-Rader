from __future__ import annotations

import os
from datetime import date, timedelta

import aiohttp

from trend_radar.collectors.base import BaseCollector
from trend_radar.config.schema import AppConfig
from trend_radar.models import CollectorResult, TrendItem
from trend_radar.utils import detect_language


class NaverDataLabCollector(BaseCollector):
    name = "naver_datalab"
    endpoint = "https://openapi.naver.com/v1/datalab/search"

    def is_available(self) -> bool:
        return True

    async def collect(self, config: AppConfig, session: aiohttp.ClientSession) -> CollectorResult:
        result = CollectorResult(name=self.name)
        collector_config = config.collectors.naver_datalab
        client_id = os.getenv(collector_config.client_id_env)
        client_secret = os.getenv(collector_config.client_secret_env)
        if not client_id or not client_secret:
            result.skipped = True
            result.warnings.append("Naver DataLab skipped: missing NAVER_CLIENT_ID/NAVER_CLIENT_SECRET.")
            return result.finish()
        keywords = collector_config.keyword_groups or config.interests.keywords or config.output.alerts.keywords
        payload = self._build_payload(keywords[: max(1, collector_config.max_items)])
        headers = {
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
            "Content-Type": "application/json",
        }
        try:
            async with session.post(self.endpoint, json=payload, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
            result.items = self._parse_response(data)
        except Exception as exc:  # pragma: no cover
            result.warnings.append(f"Naver DataLab skipped: {exc}")
        return result.finish()

    @staticmethod
    def _build_payload(keywords: list[str]) -> dict:
        today = date.today()
        start = today - timedelta(days=6)
        groups = [{"groupName": keyword, "keywords": [keyword]} for keyword in keywords if keyword]
        if not groups:
            groups = [{"groupName": "AI", "keywords": ["AI"]}]
        return {
            "startDate": start.isoformat(),
            "endDate": today.isoformat(),
            "timeUnit": "date",
            "keywordGroups": groups,
        }

    @staticmethod
    def _parse_response(payload: dict) -> list[TrendItem]:
        items: list[TrendItem] = []
        for index, row in enumerate(payload.get("results", []), start=1):
            series = row.get("data", [])
            latest_ratio = 0.0
            if series:
                latest_ratio = float(series[-1].get("ratio", 0.0))
            title = row.get("title", "")
            items.append(
                TrendItem(
                    platform="naver_datalab",
                    item_id=f"naver-{index}-{title.casefold().replace(' ', '-')}",
                    title=title,
                    url="https://datalab.naver.com/",
                    description="Naver DataLab keyword trend",
                    metrics={"ratio": latest_ratio, "points": len(series)},
                    keywords=[title],
                    category="search",
                    language=detect_language(title),
                    trend_score=min(100.0, round(latest_ratio, 2)),
                    source_type="search_term",
                )
            )
        return items
