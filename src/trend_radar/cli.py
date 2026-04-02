from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import click
import yaml

from trend_radar.config import AppConfig, dump_config, load_config
from trend_radar.diagnostics import build_doctor_report
from trend_radar import __version__
from trend_radar.runner import generate_today_digest, load_status, run_once


def main() -> None:
    cli()


def safe_echo(text: str) -> None:
    try:
        click.echo(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "utf-8"
        click.echo(text.encode(encoding, errors="replace").decode(encoding, errors="replace"))


def emit_json(payload: object) -> None:
    safe_echo(json.dumps(payload, ensure_ascii=False, indent=2))


@click.group()
@click.option("--config", "config_path", type=click.Path(path_type=Path), default=None, help="Path to config.yaml.")
@click.version_option(version=__version__, prog_name="trend-radar")
@click.pass_context
def cli(ctx: click.Context, config_path: Path | None) -> None:
    config, resolved = load_config(config_path=config_path)
    ctx.obj = {"config": config, "config_path": resolved or config_path}


@cli.command()
@click.option("--path", "config_path", type=click.Path(path_type=Path), default=Path("config.yaml"))
def init(config_path: Path) -> None:
    keywords = click.prompt("Interest keywords (comma-separated)", default="AI, startup, creator")
    categories = click.prompt("Interest categories (comma-separated)", default="tech, business, lifestyle")
    output_dir = click.prompt("Output directory", default="~/.22b/trends")
    include_rss = click.confirm("Enable generic RSS feeds?", default=True)

    feed_entries = [
        {"name": "Hacker News", "url": "https://hnrss.org/frontpage"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
    ]
    payload = {
        "interests": {
            "keywords": [value.strip() for value in keywords.split(",") if value.strip()],
            "categories": [value.strip() for value in categories.split(",") if value.strip()],
        },
        "output": {"base_dir": output_dir},
        "collectors": {
            "rss_generic": {"enabled": include_rss, "feeds": feed_entries if include_rss else []},
        },
    }
    config = AppConfig.model_validate(payload)
    destination = dump_config(config, config_path)
    click.echo(f"Created config at {destination}")


@cli.group()
def config() -> None:
    """Config helpers."""


@config.command("show")
@click.option("--json", "json_output", is_flag=True, default=False, help="Print machine-readable JSON.")
@click.pass_context
def config_show(ctx: click.Context, json_output: bool) -> None:
    config: AppConfig = ctx.obj["config"]
    payload = config.model_dump(mode="python")
    if json_output:
        emit_json(payload)
        return
    safe_echo(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False).strip())


@cli.command()
@click.option("--once", is_flag=True, default=False, help="Run collectors once.")
@click.option("--source", default=None, help="Run only one collector.")
@click.option("--output-dir", type=click.Path(path_type=Path), default=None, help="Override output directory.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Print machine-readable JSON.")
@click.pass_context
def run(ctx: click.Context, once: bool, source: str | None, output_dir: Path | None, json_output: bool) -> None:
    if not once:
        raise click.UsageError("Only --once is implemented in v0.2.0.")
    config: AppConfig = ctx.obj["config"]
    report = asyncio.run(run_once(config=config, output_dir=output_dir, source=source))
    if json_output:
        emit_json(report.to_dict())
        return
    click.echo(f"Collected {report.total_items} items into {report.output_dir}")
    click.echo(f"Index: {report.index_path}")
    if report.digest_path:
        click.echo(f"Digest: {report.digest_path}")
    for warning in report.warnings:
        click.echo(f"Warning: {warning}")


@cli.command()
@click.option("--output-dir", type=click.Path(path_type=Path), default=None, help="Override output directory.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Print machine-readable JSON.")
@click.pass_context
def status(ctx: click.Context, output_dir: Path | None, json_output: bool) -> None:
    config: AppConfig = ctx.obj["config"]
    data = load_status(config=config, output_dir=output_dir)
    if json_output:
        emit_json(data)
        return
    if not data["has_run"]:
        click.echo(f"No runs yet. Output dir: {data['output_dir']}")
        click.echo(f"Enabled collectors: {', '.join(data['active_collectors'])}")
        return
    click.echo(f"Output dir: {data['output_dir']}")
    click.echo(f"Last run: {data['generated_at']}")
    click.echo(f"Total items: {data['total_items']}")
    click.echo(f"Platforms: {', '.join(data['active_collectors'])}")


@cli.command()
@click.option("--output-dir", type=click.Path(path_type=Path), default=None, help="Override output directory.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Print machine-readable JSON.")
@click.pass_context
def doctor(ctx: click.Context, output_dir: Path | None, json_output: bool) -> None:
    config: AppConfig = ctx.obj["config"]
    config_path: Path | None = ctx.obj.get("config_path")
    report = build_doctor_report(config=config, config_path=config_path, output_dir=output_dir)
    if json_output:
        emit_json(report)
        return
    for row in report:
        safe_echo(f"[{row['status'].upper()}] {row['check']}: {row['detail']}")


@cli.group()
def digest() -> None:
    """Digest helpers."""


@digest.command("today")
@click.option("--output-dir", type=click.Path(path_type=Path), default=None, help="Override output directory.")
@click.option("--json", "json_output", is_flag=True, default=False, help="Print machine-readable JSON.")
@click.pass_context
def digest_today(ctx: click.Context, output_dir: Path | None, json_output: bool) -> None:
    config: AppConfig = ctx.obj["config"]
    digest_path = generate_today_digest(config=config, output_dir=output_dir)
    if json_output:
        emit_json({"path": str(digest_path), "content": digest_path.read_text(encoding="utf-8")})
        return
    safe_echo(digest_path.read_text(encoding="utf-8"))
