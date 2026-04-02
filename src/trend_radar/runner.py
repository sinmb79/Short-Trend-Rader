from __future__ import annotations

import asyncio
import json
from collections import Counter
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Iterable

import aiohttp

from trend_radar.collectors import (
    GoogleTrendsCollector,
    NaverDataLabCollector,
    RedditCollector,
    RSSGenericCollector,
    YouTubeCollector,
)
from trend_radar.config import AppConfig
from trend_radar.models import CollectorResult, RunReport, TrendItem, now_iso
from trend_radar.outputs import (
    build_daily_digest,
    load_items_for_date,
    write_index,
    write_platform_json,
    write_platform_markdown,
    write_run_state,
)
from trend_radar.utils import (
    compute_trend_score,
    detect_language,
    expand_path,
    extract_hashtags,
    extract_keywords,
    infer_category,
)


def create_collector_registry() -> dict[str, object]:
    return {
        "youtube": YouTubeCollector(),
        "reddit": RedditCollector(),
        "google_trends": GoogleTrendsCollector(),
        "rss_generic": RSSGenericCollector(),
        "naver_datalab": NaverDataLabCollector(),
    }


async def run_once(config: AppConfig, output_dir: str | Path | None = None, source: str | None = None) -> RunReport:
    resolved_output_dir = expand_path(output_dir or config.output.base_dir)
    selected_collectors = resolve_collectors(config=config, source=source)
    collectors: dict[str, CollectorResult] = {}
    warnings: list[str] = []
    errors: list[str] = []
    timeout = aiohttp.ClientTimeout(total=45)
    async with aiohttp.ClientSession(timeout=timeout, headers={"User-Agent": "trend-radar/0.1"}) as session:
        tasks = [run_collector(name=name, collector=collector, config=config, session=session) for name, collector in selected_collectors]
        for result in await asyncio.gather(*tasks):
            collectors[result.name] = result
            warnings.extend(result.warnings)
            errors.extend(result.errors)

    items = normalize_items(flatten(result.items for result in collectors.values()), config=config)
    day = date.today().isoformat()
    by_platform: dict[str, list[TrendItem]] = {}
    for item in items:
        by_platform.setdefault(item.platform, []).append(item)

    if "json" in config.output.formats:
        for platform, group in by_platform.items():
            write_platform_json(output_dir=resolved_output_dir, platform=platform, day=day, items=group)
    if "md" in config.output.formats:
        for platform, group in by_platform.items():
            write_platform_markdown(output_dir=resolved_output_dir, platform=platform, day=day, items=group)

    top_keywords = summarize_keywords(items)
    alerts = build_alerts(items=items, config=config)
    generated_at = now_iso()
    index_payload = {
        "generated_at": generated_at,
        "version": "0.1.0",
        "summary": {
            "total_items_collected": len(items),
            "platforms_active": sorted(by_platform),
            "top_keywords": top_keywords,
            "alerts": alerts,
        },
        "items": [
            {
                "platform": item.platform,
                "item_id": item.item_id,
                "title": item.title,
                "url": item.url,
                "keywords": item.keywords,
                "trend_score": item.trend_score,
                "category": item.category,
                "collected_at": item.collected_at,
            }
            for item in sorted(items, key=lambda row: row.trend_score or 0.0, reverse=True)
        ],
    }
    index_path = write_index(output_dir=resolved_output_dir, payload=index_payload)
    write_run_state(output_dir=resolved_output_dir, collectors=collectors, total_items=len(items), generated_at=generated_at)
    digest_path = None
    if config.output.digest:
        digest_path = str(
            build_daily_digest(
                output_dir=resolved_output_dir,
                items=items,
                top_keywords=top_keywords,
                alerts=alerts,
                day=day,
            )
        )
    return RunReport(
        output_dir=str(resolved_output_dir),
        total_items=len(items),
        collectors=collectors,
        index_path=str(index_path),
        digest_path=digest_path,
        warnings=warnings,
        errors=errors,
    )


def load_status(config: AppConfig, output_dir: str | Path | None = None) -> dict:
    resolved_output_dir = expand_path(output_dir or config.output.base_dir)
    run_state_path = resolved_output_dir / "run-state.json"
    index_path = resolved_output_dir / "index.json"
    if not run_state_path.exists() or not index_path.exists():
        return {
            "output_dir": str(resolved_output_dir),
            "has_run": False,
            "active_collectors": list(resolve_collector_names(config=config)),
        }
    run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
    index_payload = json.loads(index_path.read_text(encoding="utf-8"))
    return {
        "output_dir": str(resolved_output_dir),
        "has_run": True,
        "generated_at": run_state.get("generated_at"),
        "total_items": run_state.get("total_items", 0),
        "active_collectors": index_payload.get("summary", {}).get("platforms_active", []),
        "collector_health": run_state.get("collectors", {}),
    }


def generate_today_digest(config: AppConfig, output_dir: str | Path | None = None) -> Path:
    resolved_output_dir = expand_path(output_dir or config.output.base_dir)
    items = load_items_for_date(output_dir=resolved_output_dir)
    top_keywords = summarize_keywords(items)
    alerts = build_alerts(items=items, config=config)
    return build_daily_digest(
        output_dir=resolved_output_dir,
        items=items,
        top_keywords=top_keywords,
        alerts=alerts,
    )


async def run_collector(name: str, collector: object, config: AppConfig, session: aiohttp.ClientSession) -> CollectorResult:
    if not getattr(collector, "is_available")():
        result = CollectorResult(name=name, skipped=True, warnings=[f"{name} skipped: collector unavailable in this environment."])
        return result.finish()
    try:
        return await getattr(collector, "collect")(config, session)
    except Exception as exc:
        failed = CollectorResult(name=name, skipped=True, errors=[str(exc)])
        return failed.finish()


def resolve_collectors(config: AppConfig, source: str | None = None) -> list[tuple[str, object]]:
    registry = create_collector_registry()
    if source:
        collector = registry.get(source)
        if collector is None:
            raise ValueError(f"Unknown source: {source}")
        return [(source, collector)]
    enabled: list[tuple[str, object]] = []
    for name, collector in registry.items():
        enabled_flag = getattr(config.collectors, name).enabled
        if enabled_flag:
            enabled.append((name, collector))
    return enabled


def resolve_collector_names(config: AppConfig) -> Iterable[str]:
    for name in create_collector_registry():
        if getattr(config.collectors, name).enabled:
            yield name


def flatten(groups: Iterable[list[TrendItem]]) -> list[TrendItem]:
    items: list[TrendItem] = []
    for group in groups:
        items.extend(group)
    return items


def normalize_items(items: list[TrendItem], config: AppConfig) -> list[TrendItem]:
    normalized: list[TrendItem] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        key = (item.platform, item.item_id)
        if key in seen:
            continue
        seen.add(key)
        hashtags = item.hashtags or extract_hashtags(item.title, item.description)
        keywords = item.keywords or extract_keywords(item.title, item.description, hashtags)
        category = item.category if item.category != "general" else infer_category(
            f"{item.title} {item.description}",
            configured_categories=config.interests.categories,
        )
        language = item.language if item.language != "und" else detect_language(f"{item.title} {item.description}")
        trend_score = item.trend_score if item.trend_score is not None else compute_trend_score(item.metrics)
        normalized.append(
            replace(
                item,
                hashtags=hashtags,
                keywords=keywords,
                category=category,
                language=language,
                trend_score=trend_score,
            )
        )
    return normalized


def summarize_keywords(items: list[TrendItem], limit: int = 10) -> list[dict[str, float | str]]:
    counts: Counter[str] = Counter()
    labels: dict[str, str] = {}
    for item in items:
        for keyword in item.keywords:
            lowered = keyword.casefold()
            counts[lowered] += 1
            labels.setdefault(lowered, keyword)
    summary: list[dict[str, float | str]] = []
    for lowered, count in counts.most_common(limit):
        summary.append(
            {
                "keyword": labels[lowered],
                "score": round(min(100.0, 20.0 + (count * 12.5)), 2),
                "change_pct": 0.0,
            }
        )
    return summary


def build_alerts(items: list[TrendItem], config: AppConfig) -> list[dict[str, float | str]]:
    if not config.output.alerts.enabled:
        return []
    counts = Counter(keyword.casefold() for item in items for keyword in item.keywords)
    monitored = {keyword.casefold(): keyword for keyword in config.output.alerts.keywords}
    alerts: list[dict[str, float | str]] = []
    for lowered, original in monitored.items():
        count = counts.get(lowered, 0)
        if count >= int(config.output.alerts.spike_threshold):
            alerts.append({"keyword": original, "type": "spike", "multiplier": float(count)})
    return alerts
