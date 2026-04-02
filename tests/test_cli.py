from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from trend_radar.cli import cli


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
