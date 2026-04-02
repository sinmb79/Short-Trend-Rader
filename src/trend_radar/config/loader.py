from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from trend_radar.config.defaults import DEFAULT_CONFIG
from trend_radar.config.schema import AppConfig


def resolve_config_path(config_path: str | Path | None = None, cwd: str | Path | None = None) -> Path | None:
    if config_path:
        return Path(config_path).expanduser().resolve()
    base = Path(cwd).resolve() if cwd else Path.cwd()
    candidate = base / "config.yaml"
    return candidate if candidate.exists() else None


def load_config(config_path: str | Path | None = None, cwd: str | Path | None = None) -> tuple[AppConfig, Path | None]:
    resolved = resolve_config_path(config_path=config_path, cwd=cwd)
    merged: dict[str, Any] = deepcopy(DEFAULT_CONFIG)
    if resolved and resolved.exists():
        user_payload = yaml.safe_load(resolved.read_text(encoding="utf-8")) or {}
        merged = deep_merge(merged, user_payload)
    return AppConfig.model_validate(merged), resolved


def dump_config(config: AppConfig, destination: str | Path) -> Path:
    target = Path(destination).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = yaml.safe_dump(
        config.model_dump(mode="python"),
        allow_unicode=True,
        sort_keys=False,
    )
    target.write_text(payload, encoding="utf-8")
    return target


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged
