from __future__ import annotations

from pathlib import Path

import pytest

from trend_radar.config import AppConfig


@pytest.fixture()
def app_config(tmp_path: Path) -> AppConfig:
    return AppConfig.model_validate(
        {
            "output": {"base_dir": str(tmp_path / "trends"), "formats": ["md", "json"], "digest": True},
            "collectors": {
                "youtube": {"enabled": True, "regions": ["US"], "categories": ["trending"], "max_items": 5},
                "reddit": {"enabled": True, "subreddits": ["technology"], "max_items": 5},
                "google_trends": {"enabled": True, "regions": ["US"], "max_items": 5},
                "rss_generic": {
                    "enabled": True,
                    "feeds": [{"name": "Hacker News", "url": "https://hnrss.org/frontpage"}],
                    "max_items": 5,
                },
                "naver_datalab": {"enabled": True, "max_items": 5},
            },
        }
    )
