from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from trend_radar.cli import cli
from trend_radar.models import CollectorResult, RunReport


def test_init_creates_config_file(tmp_path: Path) -> None:
    runner = CliRunner()
    config_path = tmp_path / "config.yaml"
    result = runner.invoke(
        cli,
        ["init", "--path", str(config_path)],
        input="AI, robotics\ntech, business\n~/.22b/test-trends\ny\n",
    )
    assert result.exit_code == 0
    assert config_path.exists()


def test_status_without_runs_uses_defaults(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--config", str(tmp_path / "missing.yaml"), "status", "--output-dir", str(tmp_path / "out")])
    assert result.exit_code == 0
    assert "No runs yet" in result.output


def test_version_option() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "trend-radar" in result.output


def test_run_once_can_print_machine_readable_json(tmp_path: Path, monkeypatch) -> None:
    async def fake_run_once(config, output_dir=None, source=None) -> RunReport:
        return RunReport(
            output_dir=str(tmp_path / "out"),
            total_items=3,
            collectors={"youtube": CollectorResult(name="youtube").finish()},
            index_path=str(tmp_path / "out" / "index.json"),
            digest_path=str(tmp_path / "out" / "digest" / "daily.md"),
        )

    runner = CliRunner()
    monkeypatch.setattr("trend_radar.cli.run_once", fake_run_once)

    result = runner.invoke(
        cli,
        ["--config", str(tmp_path / "missing.yaml"), "run", "--once", "--json", "--output-dir", str(tmp_path / "out")],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["total_items"] == 3
    assert payload["collectors"]["youtube"]["item_count"] == 0


def test_status_can_print_machine_readable_json(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["--config", str(tmp_path / "missing.yaml"), "status", "--json", "--output-dir", str(tmp_path / "out")],
    )
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["has_run"] is False
    assert payload["output_dir"].endswith("out")


def test_digest_today_can_print_machine_readable_json(tmp_path: Path, monkeypatch) -> None:
    digest_path = tmp_path / "digest.md"
    digest_path.write_text("# Digest\n", encoding="utf-8")

    runner = CliRunner()
    monkeypatch.setattr("trend_radar.cli.generate_today_digest", lambda config, output_dir=None: digest_path)

    result = runner.invoke(
        cli,
        ["--config", str(tmp_path / "missing.yaml"), "digest", "today", "--json", "--output-dir", str(tmp_path / "out")],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["path"] == str(digest_path)
    assert payload["content"] == "# Digest\n"
