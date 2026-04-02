from __future__ import annotations

from pathlib import Path

from trend_radar.models import TrendItem
from trend_radar.utils import compact_join


def write_platform_markdown(output_dir: Path, platform: str, day: str, items: list[TrendItem]) -> Path:
    target = output_dir / "feeds" / platform / f"{day}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {platform} feed", "", f"- Date: {day}", f"- Items: {len(items)}", ""]
    for index, item in enumerate(items, start=1):
        lines.append(f"## {index}. {item.title}")
        lines.append(f"- URL: {item.url}")
        lines.append(f"- Author: {item.author or '-'}")
        lines.append(f"- Category: {item.category}")
        lines.append(f"- Keywords: {compact_join(item.keywords)}")
        lines.append(f"- Trend score: {item.trend_score if item.trend_score is not None else '-'}")
        if item.description:
            lines.append(f"- Summary: {item.description[:240]}")
        lines.append("")
    target.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return target
