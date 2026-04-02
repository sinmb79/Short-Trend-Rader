from __future__ import annotations

from click.testing import CliRunner

from trend_radar.cli import cli
from trend_radar.diagnostics import build_doctor_report


def test_doctor_command_prints_checks(app_config, tmp_path) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["doctor", "--output-dir", str(tmp_path / "out")])
    assert result.exit_code == 0
    assert "[OK] python:" in result.output
    assert "collector:youtube" in result.output


def test_doctor_report_warns_when_naver_credentials_missing(app_config) -> None:
    report = build_doctor_report(config=app_config, config_path=None, output_dir=app_config.output.base_dir)
    row = next(item for item in report if item["check"] == "collector:naver_datalab")
    assert row["status"] == "warn"
