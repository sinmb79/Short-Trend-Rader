from __future__ import annotations

import asyncio

import pytest

from trend_radar.collectors.base import BaseCollector
from trend_radar.models import CollectorResult, TrendItem
from trend_radar.runner import generate_today_digest, run_once


class SuccessCollector(BaseCollector):
    name = "success"

    def is_available(self) -> bool:
        return True

    async def collect(self, config, session) -> CollectorResult:
        item = TrendItem(
            platform="success",
            item_id="item-1",
            title="AI makers are shipping",
            url="https://example.com/1",
            description="#AI goes local",
            metrics={"views": 10_000},
        )
        return CollectorResult(name=self.name, items=[item]).finish()


class FailingCollector(BaseCollector):
    name = "failing"

    def is_available(self) -> bool:
        return True

    async def collect(self, config, session) -> CollectorResult:
        raise RuntimeError("network down")


@pytest.mark.asyncio
async def test_run_once_writes_outputs_and_survives_collector_failure(app_config, monkeypatch) -> None:
    monkeypatch.setattr(
        "trend_radar.runner.resolve_collectors",
        lambda config, source=None: [("success", SuccessCollector()), ("failing", FailingCollector())],
    )
    report = await run_once(config=app_config)
    assert report.total_items == 1
    assert report.index_path.endswith("index.json")
    assert report.collectors["failing"].errors == ["network down"]
    assert report.digest_path is not None


def test_generate_today_digest_reads_feed_files(app_config, monkeypatch) -> None:
    monkeypatch.setattr(
        "trend_radar.runner.resolve_collectors",
        lambda config, source=None: [("success", SuccessCollector())],
    )
    asyncio.run(run_once(config=app_config))
    digest_path = generate_today_digest(config=app_config)
    assert digest_path.exists()
    assert "Top Keywords" in digest_path.read_text(encoding="utf-8")
