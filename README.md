# Short-Trend-Rader

왜 이 저장소가 존재하나. 대부분의 트렌드 작업은 데이터를 못 모아서 실패하지 않습니다. 모은 뒤에 정리되지 않아서 실패합니다. 누군가는 링크를 모으고, 누군가는 따로 메모를 쓰고, 누군가는 나중에 다시 검색합니다. 그 사이에 타이밍이 사라집니다. `trend-radar`는 그 틈을 줄이기 위해 만들어졌습니다. 공개된 트렌드 신호를 한 번 모아서, 사람이 읽을 수 있는 Markdown과 다른 도구가 읽을 수 있는 JSON으로 같은 자리에 남깁니다.

Why this repository exists. Most trend workflows do not fail because people cannot find data. They fail because the handoff is messy. One person collects links, another writes notes somewhere else, and a third person has to search the web again later. By then, the timing is gone. `trend-radar` exists to reduce that gap. It collects public trend signals once, then leaves them behind as Markdown for humans and JSON for tools.

Meta description: Public trend intelligence CLI for collecting YouTube, Reddit, Google Trends, and RSS signals into reusable Markdown and JSON feeds.

Labels: python, trend-intelligence, cli, youtube, reddit, google-trends, rss, 22b-labs

Author: 22B Labs · The 4th Path | GitHub: `sinmb79`

중요한 이름 설명부터 먼저 드리겠습니다. GitHub 저장소 이름은 `Short-Trend-Rader`지만, 실제 Python 패키지와 CLI 이름은 `trend-radar`입니다. 저장소 이름은 공개 배포 주소이고, 실행 이름은 사용자가 터미널에서 쓰는 이름이라고 이해하시면 됩니다.

One naming note up front. The GitHub repository is named `Short-Trend-Rader`, but the Python package and CLI are named `trend-radar`. Think of the repository name as the public address, and the CLI name as the tool name people type in the terminal.

## 30초 이해 / Understand It In 30 Seconds

한 줄로 말하면, 이 시스템은 “트렌드 수집을 표준화해서 다른 작업들이 재사용할 수 있게 만드는 로컬 정보 레이어”입니다.

In one line, this system is a local intelligence layer that standardizes trend collection so other work can reuse it.

아주 쉽게 풀면 아래와 같습니다.

Here is the plain-language version.

- YouTube, Reddit, Google Trends, RSS 같은 공개 소스에서 데이터를 모읍니다.
- 결과를 `~/.22b/trends` 아래에 날짜별 파일로 저장합니다.
- 사용자는 Markdown으로 읽고, 다른 도구는 JSON으로 읽습니다.
- 같은 데이터를 다시 긁지 않아도 되기 때문에 후속 자동화가 쉬워집니다.

- It collects from public sources such as YouTube, Reddit, Google Trends, and RSS.
- It saves the result as dated files under `~/.22b/trends`.
- Humans read the Markdown files, and tools read the JSON files.
- Because the data is collected once and reused many times, follow-up automation becomes simpler.

## 시스템 구조 / System Structure

신입 분에게 설명하듯이 아주 단순하게 구조를 나누면, 이 프로젝트는 네 층으로 이해하시면 됩니다.

If I were explaining this to a new teammate, I would divide the system into four layers.

1. `collectors`
   한국어: 각 플랫폼에서 데이터를 가져오는 모듈입니다. YouTube, Reddit, Google Trends, RSS, Naver DataLab이 여기에 들어갑니다.
   English: These modules fetch data from each source. YouTube, Reddit, Google Trends, RSS, and Naver DataLab live here.
2. `runner`
   한국어: 어떤 수집기를 실행할지 결정하고, 동시에 돌리고, 실패를 모아서 정리하는 오케스트레이터입니다.
   English: This is the orchestrator. It decides which collectors to run, executes them together, and gathers warnings or failures.
3. `outputs`
   한국어: 수집된 결과를 Markdown, JSON, digest 파일로 쓰는 계층입니다.
   English: This layer writes the collected results into Markdown files, JSON files, and digest files.
4. `cli`
   한국어: 사용자가 실제로 만나는 입구입니다. `init`, `run --once`, `status`, `digest today`, `doctor` 같은 명령이 여기서 시작됩니다.
   English: This is the entry point users interact with. Commands like `init`, `run --once`, `status`, `digest today`, and `doctor` begin here.

이 구조가 중요한 이유는, 나중에 TikTok을 붙이더라도 CLI를 갈아엎지 않아도 되고, digest를 바꾸더라도 수집기를 다시 쓰지 않아도 되기 때문입니다. 바꿀 수 있는 부분과 고정해야 하는 부분을 분리해 두는 것이 장기적으로 훨씬 싸게 먹힙니다.

This structure matters because it keeps change localized. If we add TikTok later, we should not need to rewrite the CLI. If we change the digest logic later, we should not need to rewrite the collectors. Separating changeable parts from stable contracts is cheaper in the long run.

## 데이터 흐름 / Data Flow

실행 흐름은 아래 순서로 이해하시면 됩니다.

Here is the runtime flow in the order it actually happens.

1. 사용자가 `trend-radar run --once`를 실행합니다.
   The user runs `trend-radar run --once`.
2. 시스템이 기본 설정과 `config.yaml`을 합쳐 최종 설정을 만듭니다.
   The system merges built-in defaults with `config.yaml` to build the final config.
3. 활성화된 수집기만 골라 병렬로 실행합니다.
   It selects only enabled collectors and runs them in parallel.
4. 각 수집기는 플랫폼별 응답을 `TrendItem`이라는 공용 데이터 형태로 바꿉니다.
   Each collector converts source-specific responses into a shared `TrendItem` shape.
5. 러너가 중복을 제거하고, 키워드와 카테고리 같은 공통 필드를 보정합니다.
   The runner removes duplicates and normalizes shared fields such as keywords and categories.
6. 결과를 플랫폼별 Markdown과 JSON으로 저장합니다.
   The system writes platform-specific Markdown and JSON files.
7. 전체 요약용 `index.json`과 읽기 쉬운 daily digest를 생성합니다.
   It builds the shared `index.json` and a human-readable daily digest.
8. 마지막 실행 상태를 `run-state.json`에 남겨서 `status`와 `doctor`가 참고할 수 있게 합니다.
   It stores run metadata in `run-state.json` so `status` and `doctor` have something to inspect.

중요한 철학 하나를 여기서 기억하시면 좋습니다. 이 프로젝트는 아직 “완벽한 분석기”가 아니라 “믿을 수 있는 수집과 전달기”를 먼저 만드는 단계입니다. 분석보다 전달 계약을 먼저 고정하는 것이 더 맞는 순서입니다.

One important design philosophy belongs here. This project is still in the stage of becoming a reliable collector and distributor before it becomes a perfect analyzer. Locking the delivery contract first is a more correct order than chasing smarter analysis too early.

## 폴더 구조 / Directory Layout

현재 저장소는 아래처럼 이해하시면 됩니다.

Here is how to read the repository today.

```text
Short-Trend-Rader/
  src/trend_radar/
    cli.py
    diagnostics.py
    runner.py
    scheduler.py
    models.py
    utils.py
    collectors/
    config/
    outputs/
  tests/
  docs/
  config.example.yaml
  pyproject.toml
  README.md
```

- `src/trend_radar/collectors`
  한국어: 소스별 수집 로직입니다.
  English: Source-specific collection logic.
- `src/trend_radar/config`
  한국어: 기본 설정, 스키마, 파일 로더입니다.
  English: Defaults, schema models, and config loading.
- `src/trend_radar/outputs`
  한국어: 결과 파일을 쓰는 계층입니다.
  English: File writers for outputs and digests.
- `tests`
  한국어: 파서, CLI, 설정, 러너를 검증하는 테스트입니다.
  English: Tests for parsers, CLI behavior, config loading, and the runner.
- `docs`
  한국어: 공개 저장소 독자를 위한 설명 문서입니다.
  English: Documentation for public readers of the repository.

## 지금 지원하는 데이터 소스 / Current Data Sources

현재 기본 동작으로 바로 쓸 수 있는 소스와, 추가 설정이 필요한 소스를 구분해서 보시면 이해가 쉽습니다.

It is easiest to understand the sources by splitting them into zero-config defaults and optional sources.

기본 소스입니다.

These are the default sources.

- YouTube
  한국어: 공개 페이지 기반으로 트렌딩과 Shorts 성격의 항목을 수집합니다.
  English: Collects trending and Shorts-like items from public YouTube pages.
- Reddit
  한국어: 서브레딧의 공개 JSON 엔드포인트를 사용합니다.
  English: Uses public subreddit JSON endpoints.
- Google Trends
  한국어: RSS 기반으로 안정적으로 수집하고, 필요 시 `pytrends`를 보조로 사용할 수 있게 구성했습니다.
  English: Uses RSS as the stable path, with `pytrends` available as a fallback path.
- Generic RSS
  한국어: 사용자가 원하는 피드를 직접 추가할 수 있습니다.
  English: Lets users add any RSS or Atom feeds they care about.

선택 소스입니다.

This is the optional source.

- Naver DataLab
  한국어: 지원은 하지만 `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` 환경변수가 있어야 실제 실행됩니다.
  English: Supported, but it only runs when `NAVER_CLIENT_ID` and `NAVER_CLIENT_SECRET` are present.

의도적으로 아직 넣지 않은 것들도 있습니다. TikTok, Instagram, X/Twitter, Whisper 기반 전사, 장기 daemon 운영은 후속 단계입니다. 하지 못해서 뺀 것이 아니라, 공개 배포 시점에서 기본 경로를 안정적으로 유지하기 위해 뒤로 미룬 것입니다.

Some things are intentionally not included yet. TikTok, Instagram, X/Twitter, Whisper transcription, and long-running daemon mode are later steps. They were not excluded because they are impossible. They were deferred to keep the public default path stable at release time.

## 설치와 첫 실행 / Installation And First Run

가장 권장하는 경로는 Poetry를 사용하는 것입니다.

The recommended path is to use Poetry.

```bash
poetry install
poetry run trend-radar doctor
poetry run trend-radar init
poetry run trend-radar run --once
poetry run trend-radar digest today
```

Poetry가 아직 없다면 Python만으로도 시작할 수 있습니다.

If Poetry is not installed yet, you can still start with plain Python.

```bash
python -m pip install --user --no-cache-dir -e .
python -m trend_radar doctor
python -m trend_radar init
python -m trend_radar run --once
python -m trend_radar digest today
```

이때 `doctor`를 먼저 돌리는 이유는 아주 단순합니다. 신입이 가장 많이 겪는 문제는 “코드가 고장 난 것 같지만 사실은 환경이 비어 있는 상황”입니다. `doctor`는 그 혼란을 줄이기 위해 만들었습니다.

There is a simple reason to run `doctor` first. The most common beginner problem is thinking the code is broken when the environment is simply incomplete. `doctor` exists to reduce that confusion.

## 주요 명령 설명 / Command Guide

처음에는 아래 명령만 알아도 충분합니다.

At the beginning, these commands are enough.

- `trend-radar init`
  한국어: 대화형으로 `config.yaml`을 만듭니다.
  English: Creates `config.yaml` interactively.
- `trend-radar run --once`
  한국어: 현재 설정으로 한 번 수집하고 결과 파일을 씁니다.
  English: Runs one collection pass and writes the output files.
- `trend-radar config show`
  한국어: 기본값과 사용자 설정이 합쳐진 최종 설정을 보여줍니다.
  English: Shows the merged effective configuration.
- `trend-radar status`
  한국어: 최근 실행 시각, 활성 플랫폼, 수집 건수를 보여줍니다.
  English: Shows the last run time, active platforms, and item count.
- `trend-radar digest today`
  한국어: 오늘 수집된 결과를 요약해서 읽기 쉬운 형태로 출력합니다.
  English: Prints a readable digest based on today’s collected data.
- `trend-radar doctor`
  한국어: Python 버전, config 존재 여부, 출력 경로, 선택 소스 환경변수를 점검합니다.
  English: Checks Python version, config presence, output path, and optional source credentials.

## n8n 연동 / n8n Integration

이 저장소는 CLI만 있는 프로젝트처럼 보이지만, 사실 그래서 더 n8n과 잘 맞습니다.  
English: This repository may look like a CLI-first project, and that is exactly why it fits n8n well.

핵심은 n8n이 코드를 대체하는 것이 아니라, 이미 잘 만든 CLI를 반복 가능하고 연결 가능한 워크플로우로 감싸는 데 있습니다.  
English: The point is not to replace code with n8n, but to wrap a solid CLI in repeatable, connectable workflows.

`n8n/` 디렉터리에는 바로 import할 수 있는 워크플로우와 자세한 연동 문서가 들어 있습니다.  
English: The `n8n/` directory now includes import-ready workflows and a detailed integration guide.

- `n8n/workflow.json`
  한국어: 수동 실행, 웹훅 실행, 예약 실행을 한 워크플로우에 묶은 기본 수집 플로우입니다.
  English: The main collection workflow covering manual, webhook, and scheduled runs.
- `n8n/workflow-digest.json`
  한국어: 일일 digest 생성에 집중한 보조 워크플로우입니다.
  English: A companion workflow focused on daily digest generation.
- `n8n/README.md`
  한국어: 설치, import, 입력값, 경로 수정, 보안 주의사항까지 신입 온보딩처럼 설명한 가이드입니다.
  English: A Korean-first bilingual guide that walks through setup, import, inputs, path edits, and security notes.

자동화 친화성을 위해 `run`, `status`, `doctor`, `digest today`, `config show`는 이제 `--json` 출력도 지원합니다.  
English: For automation, `run`, `status`, `doctor`, `digest today`, and `config show` now support `--json` output as well.

## 출력 파일은 어떻게 읽나 / How To Read The Output

기본 출력 위치는 `~/.22b/trends`입니다.

The default output directory is `~/.22b/trends`.

핵심 파일은 아래 다섯 가지입니다.

These are the five files new users should care about first.

- `feeds/<platform>/<YYYY-MM-DD>.json`
  한국어: 플랫폼별 원본에 가까운 구조화 데이터입니다.
  English: Structured platform-specific data, closer to the raw collection result.
- `feeds/<platform>/<YYYY-MM-DD>.md`
  한국어: 사람이 훑어보기 쉬운 플랫폼 요약입니다.
  English: A human-readable per-platform summary.
- `digest/daily-<YYYY-MM-DD>.md`
  한국어: 오늘 무엇이 모였는지 빠르게 읽는 일일 브리프입니다.
  English: A daily brief that lets you scan what was collected today.
- `index.json`
  한국어: 다른 22B Labs 도구가 읽기 위한 공용 요약 인덱스입니다.
  English: The shared summary index that other 22B Labs tools can consume.
- `run-state.json`
  한국어: 최근 실행 상태와 수집기별 경고를 기록합니다.
  English: Stores the latest run metadata and per-collector warnings.

여기서 중요한 포인트는 Markdown과 JSON을 둘 다 쓰는 이유입니다. Markdown은 사람의 판단 속도를 올리고, JSON은 도구 간 연결 비용을 낮춥니다. 둘 중 하나만 있으면 결국 다른 쪽이 다시 생깁니다.

The important point is why both Markdown and JSON exist. Markdown increases human judgment speed, while JSON lowers integration cost between tools. If you only keep one, the other usually reappears later in a messier form.

## 설정은 어디를 만지면 되나 / What To Change In Configuration

처음에는 아래 세 군데만 바꾸셔도 충분합니다.

At first, you only need to change these three areas.

- `collectors`
  한국어: 어떤 소스를 켜고 끌지 정합니다.
  English: Controls which sources are enabled.
- `interests`
  한국어: 관심 키워드와 카테고리를 넣습니다.
  English: Stores your interest keywords and categories.
- `output.base_dir`
  한국어: 결과를 어디에 저장할지 정합니다.
  English: Sets where outputs are written.

예제는 [config.example.yaml](./config.example.yaml)에 있습니다.

See [config.example.yaml](./config.example.yaml) for a concrete example.

## 테스트와 품질 / Testing And Quality

공개 저장소에서는 “내 컴퓨터에서는 됐다”가 기준이 되면 안 됩니다. 그래서 최소한의 회귀 테스트와 GitHub Actions CI를 같이 넣어 두었습니다.

In a public repository, “it worked on my machine” is not a good enough standard. That is why this project includes regression tests and GitHub Actions CI.

테스트 실행 명령입니다.

Run the test suite with:

```bash
python -m pytest
```

CI 설정 파일은 [.github/workflows/ci.yml](./.github/workflows/ci.yml)에 있습니다.

The CI workflow lives in [.github/workflows/ci.yml](./.github/workflows/ci.yml).

## 더 자세한 온보딩 문서 / More Detailed Onboarding

조금 더 차분하게 구조와 사용법을 읽고 싶다면 아래 문서를 보시면 됩니다.

If you want a slower, more tutorial-style explanation of the structure and workflow, read the document below.

- [신입 온보딩용 시스템 가이드 / System Guide For New Team Members](./docs/system-guide-ko-en.md)
- [한국어 시작 문서 / Korean Getting Started](./docs/getting-started-ko.md)
- [English Getting Started](./docs/getting-started-en.md)

## 현재 상태 / Current Status

현재 이 프로젝트는 공개 배포 가능한 alpha입니다. 실제 수집은 이미 동작하고, 기본 명령과 테스트도 갖춰져 있습니다. 다만 “풀 스택 트렌드 운영 플랫폼”이 아니라 “재사용 가능한 수집 기반”이라는 점은 꼭 기억하시면 좋겠습니다.

This project is now in a public-release alpha state. Real collection works, the core CLI is present, and tests are in place. But it should still be understood as a reusable collection foundation, not yet a full operating trend platform.

마지막으로, 이 저장소를 볼 때 가장 중요한 관점 하나만 남기겠습니다. 좋은 시스템은 더 많은 소음을 모으는 시스템이 아니라, 신호가 사라지지 않게 붙잡아 두는 시스템입니다.

One final perspective before you leave this page. A good system is not the one that collects the most noise. It is the one that gives signal a place to survive.
