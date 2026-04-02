from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trend_radar.models import CollectorResult, TrendItem


def write_platform_json(output_dir: Path, platform: str, day: str, items: list[TrendItem]) -> Path:
    target = output_dir / "feeds" / platform / f"{day}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = [item.to_dict() for item in items]
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def write_index(output_dir: Path, payload: dict[str, Any]) -> Path:
    target = output_dir / "index.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def write_run_state(output_dir: Path, collectors: dict[str, CollectorResult], total_items: int, generated_at: str) -> Path:
    target = output_dir / "run-state.json"
    summary = {
        "generated_at": generated_at,
        "total_items": total_items,
        "collectors": {
            name: {
                "items": len(result.items),
                "warnings": result.warnings,
                "errors": result.errors,
                "skipped": result.skipped,
                "started_at": result.started_at,
                "finished_at": result.finished_at,
            }
            for name, result in collectors.items()
        },
    }
    target.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return target
