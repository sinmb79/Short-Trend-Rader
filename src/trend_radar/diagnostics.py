from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from trend_radar.config import AppConfig
from trend_radar.runner import create_collector_registry
from trend_radar.utils import expand_path


def build_doctor_report(config: AppConfig, config_path: Path | None = None, output_dir: str | Path | None = None) -> list[dict[str, str]]:
    resolved_output_dir = expand_path(output_dir or config.output.base_dir)
    rows: list[dict[str, str]] = []
    rows.append(
        {
            "check": "python",
            "status": "ok" if sys.version_info >= (3, 11) else "fail",
            "detail": f"Python {sys.version.split()[0]}",
        }
    )
    rows.append(
        {
            "check": "config",
            "status": "ok" if config_path else "warn",
            "detail": str(config_path.resolve()) if config_path else "No config.yaml found, defaults will be used.",
        }
    )
    rows.append(
        {
            "check": "poetry",
            "status": "ok" if shutil.which("poetry") else "warn",
            "detail": "Poetry found on PATH." if shutil.which("poetry") else "Poetry not found on PATH. Python module execution still works.",
        }
    )
    rows.append(
        {
            "check": "output_dir",
            "status": "ok" if is_output_path_usable(resolved_output_dir) else "fail",
            "detail": str(resolved_output_dir),
        }
    )
    rows.extend(build_collector_rows(config))
    return rows


def is_output_path_usable(path: Path) -> bool:
    if path.exists():
        return path.is_dir() and os.access(path, os.W_OK)
    parent = next((candidate for candidate in [path.parent, *path.parents] if candidate.exists()), None)
    return bool(parent and parent.is_dir() and os.access(parent, os.W_OK))


def build_collector_rows(config: AppConfig) -> list[dict[str, str]]:
    registry = create_collector_registry()
    rows: list[dict[str, str]] = []
    for name, collector in registry.items():
        collector_config = getattr(config.collectors, name)
        if not collector_config.enabled:
            rows.append({"check": f"collector:{name}", "status": "skip", "detail": "Disabled in config."})
            continue
        if name == "naver_datalab":
            client_id = os.getenv(collector_config.client_id_env)
            client_secret = os.getenv(collector_config.client_secret_env)
            if client_id and client_secret:
                rows.append({"check": f"collector:{name}", "status": "ok", "detail": "Enabled and credentials are present."})
            else:
                rows.append(
                    {
                        "check": f"collector:{name}",
                        "status": "warn",
                        "detail": f"Enabled, but {collector_config.client_id_env}/{collector_config.client_secret_env} are missing.",
                    }
                )
            continue
        if name == "rss_generic" and not collector_config.feeds:
            rows.append({"check": f"collector:{name}", "status": "warn", "detail": "Enabled, but no RSS feeds are configured."})
            continue
        available = collector.is_available()
        rows.append(
            {
                "check": f"collector:{name}",
                "status": "ok" if available else "warn",
                "detail": "Enabled and ready." if available else "Enabled, but collector reports unavailable.",
            }
        )
    return rows
