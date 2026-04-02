from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from trend_radar.models import TrendItem
from trend_radar.utils import compact_join


def load_items_for_date(output_dir: Path, day: str | None = None) -> list[TrendItem]:
    selected_day = day or date.today().isoformat()
    items: list[TrendItem] = []
    feeds_dir = output_dir / "feeds"
    if not feeds_dir.exists():
        return items
    for json_path in feeds_dir.rglob(f"{selected_day}.json"):
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        items.extend(TrendItem.from_dict(row) for row in payload)
    return items


def build_daily_digest(
    output_dir: Path,
    items: list[TrendItem],
    top_keywords: list[dict[str, float | str]],
    alerts: list[dict[str, float | str]],
    day: str | None = None,
) -> Path:
    selected_day = day or date.today().isoformat()
    target = output_dir / "digest" / f"daily-{selected_day}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    platform_groups: dict[str, list[TrendItem]] = defaultdict(list)
    for item in items:
        platform_groups[item.platform].append(item)

    lines = ["# trend-radar Daily Digest", "", f"- Date: {selected_day}", f"- Items collected: {len(items)}", ""]
    lines.append("## Top Keywords")
    if top_keywords:
        for row in top_keywords:
            lines.append(f"- {row['keyword']} | score={row['score']} | change_pct={row['change_pct']}")
    else:
        lines.append("- No keywords surfaced yet.")
    lines.append("")

    lines.append("## Platform Summary")
    if not platform_groups:
        lines.append("- No platform data for this date.")
    for platform, group in sorted(platform_groups.items()):
        lines.append(f"### {platform}")
        sorted_items = sorted(group, key=lambda item: item.trend_score or 0.0, reverse=True)
        for item in sorted_items[:5]:
            lines.append(f"- {item.title} ({item.trend_score or 0:.2f})")
            lines.append(f"  by {item.author or 'unknown'} | {compact_join(item.keywords)}")
    lines.append("")

    lines.append("## Alerts")
    if alerts:
        for alert in alerts:
            lines.append(f"- {alert['keyword']} spike x{alert['multiplier']}")
    else:
        lines.append("- No alerts.")
    lines.append("")

    keyword_counts = Counter(keyword for item in items for keyword in item.keywords)
    if keyword_counts:
        lines.append("## Keyword Counts")
        for keyword, count in keyword_counts.most_common(10):
            lines.append(f"- {keyword}: {count}")
        lines.append("")

    target.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return target
