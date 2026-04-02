# trend-radar Getting Started

## Why this project exists

`trend-radar` exists because most trend workflows die in the handoff between gathering signals and using them. This project keeps those signals as local files that both humans and tools can read.

## Install

```bash
poetry install
```

If Poetry is not available yet:

```bash
python -m pip install --user --no-cache-dir -e .
```

## First run

1. Check your environment.
   `poetry run trend-radar doctor`
2. Create a config.
   `poetry run trend-radar init`
3. Collect once.
   `poetry run trend-radar run --once`
4. Read the digest.
   `poetry run trend-radar digest today`

## Default data sources

- YouTube
- Reddit
- Google Trends
- Generic RSS

`Naver DataLab` is supported, but only when `NAVER_CLIENT_ID` and `NAVER_CLIENT_SECRET` are present.

## Output files

- `feeds/<platform>/<YYYY-MM-DD>.json`
- `feeds/<platform>/<YYYY-MM-DD>.md`
- `digest/daily-<YYYY-MM-DD>.md`
- `index.json`
- `run-state.json`

## Public release posture

- License: MIT
- Python: 3.11+
- Status: alpha
- Collection mode today: one-shot CLI
- Long-running daemon mode: intentionally deferred
