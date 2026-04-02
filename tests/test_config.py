from __future__ import annotations

from pathlib import Path

from trend_radar.config.loader import load_config


def test_load_config_merges_defaults(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
output:
  base_dir: ~/custom-trends
collectors:
  reddit:
    subreddits:
      - python
""".strip(),
        encoding="utf-8",
    )
    config, resolved = load_config(config_path=config_path)
    assert resolved == config_path.resolve()
    assert config.output.base_dir == "~/custom-trends"
    assert config.collectors.reddit.subreddits == ["python"]
    assert config.collectors.youtube.enabled is True
