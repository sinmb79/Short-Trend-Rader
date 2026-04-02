# 신입 온보딩용 시스템 가이드 / System Guide For New Team Members

## 1. 먼저 큰 그림부터 / Start With The Big Picture

한국어:
이 프로젝트를 처음 보면 “트렌드를 모으는 스크립트인가요?”라고 생각하기 쉽습니다. 반은 맞고 반은 틀립니다. 단순 스크립트라면 한 번 긁고 끝나도 됩니다. 하지만 이 프로젝트는 그보다 한 단계 위에 있습니다. 수집된 결과를 다른 도구와 사람이 함께 재사용할 수 있는 공용 형식으로 남기는 것이 목적입니다. 그래서 이 프로젝트의 진짜 역할은 스크래퍼가 아니라 “정보 전달 계층”에 가깝습니다.

English:
When people first see this project, they often think, “Is this just a script that scrapes trends?” That is only half true. A simple script can fetch something once and stop there. This project sits one level above that. Its goal is to preserve collected results in a shared format that both people and other tools can reuse. So its real role is closer to an information delivery layer than a mere scraper.

## 2. 이 시스템이 해결하는 문제 / What Problem This System Solves

한국어:
현실에서 가장 자주 생기는 문제는 수집보다 재사용입니다. 누군가 YouTube와 Reddit를 훑어보고 “요즘 이런 게 뜨네”라고 말할 수는 있습니다. 하지만 그 결과가 다음 작업으로 이어지지 않으면, 매번 같은 탐색을 반복하게 됩니다. `trend-radar`는 그 반복을 줄입니다. 오늘의 신호를 내일 다시 쓸 수 있게 만드는 것이 핵심입니다.

English:
In practice, the hardest problem is not collection. It is reuse. Someone can look through YouTube and Reddit and say, “These topics seem hot right now.” But if that result does not flow into the next task, the same exploration must be repeated again and again. `trend-radar` reduces that repetition. The key is making today’s signals reusable tomorrow.

## 3. 내부 구조를 쉬운 비유로 보기 / Understanding The Architecture With A Simple Analogy

한국어:
비유를 하나 들면 이해가 쉽습니다.

- `collectors`는 현장 취재 기자입니다.
- `runner`는 데스크 편집자입니다.
- `outputs`는 기사와 요약본을 내보내는 출판팀입니다.
- `cli`는 사용자가 데스크에 지시를 내리는 인터폰입니다.

각자가 역할을 분리해 두었기 때문에, 한 군데를 바꿀 때 다른 곳을 덜 건드리게 됩니다. 이 분리는 코드가 길어 보여도 유지보수 비용을 줄입니다.

English:
An analogy helps here.

- `collectors` are field reporters.
- `runner` is the desk editor.
- `outputs` are the publishing team producing articles and summaries.
- `cli` is the intercom where users give instructions to the desk.

Because those roles are separated, changing one area tends to disturb the others less. Even if the codebase looks more structured up front, this separation lowers long-term maintenance cost.

## 4. 실제 파일 기준으로 보기 / Reading The Codebase By File

한국어:
처음 코드를 읽을 때는 아래 순서가 좋습니다.

1. `src/trend_radar/cli.py`
   사용자가 어떤 명령을 쓸 수 있는지 봅니다.
2. `src/trend_radar/runner.py`
   실제 실행 흐름이 어떻게 이어지는지 봅니다.
3. `src/trend_radar/models.py`
   공용 데이터 형태가 어떻게 생겼는지 봅니다.
4. `src/trend_radar/collectors/*`
   플랫폼별 수집 방식이 어떻게 다른지 봅니다.
5. `src/trend_radar/outputs/*`
   결과가 어떤 파일로 저장되는지 봅니다.

이 순서가 좋은 이유는, 먼저 “사용자 입구”를 이해하고 나서 “내부 처리”를 읽는 편이 더 자연스럽기 때문입니다.

English:
When reading the code for the first time, this order works well.

1. `src/trend_radar/cli.py`
   See what commands users can run.
2. `src/trend_radar/runner.py`
   See how execution actually flows.
3. `src/trend_radar/models.py`
   Understand the shared data contract.
4. `src/trend_radar/collectors/*`
   See how source-specific collection differs by platform.
5. `src/trend_radar/outputs/*`
   See how results are saved.

This order works because understanding the user-facing entry point first makes the internal flow easier to follow.

## 5. `TrendItem`이 중요한 이유 / Why `TrendItem` Matters

한국어:
이 프로젝트에서 가장 중요한 객체는 `TrendItem`입니다. 이유는 간단합니다. YouTube 응답도 다르고, Reddit 응답도 다르고, Google Trends 응답도 모두 다릅니다. 그런데 후속 처리와 출력 단계에서는 “공통 언어”가 필요합니다. `TrendItem`은 그 공통 언어입니다. 이 계약이 흔들리면 수집기와 출력기, 그리고 나중에 붙을 다른 도구까지 전부 흔들립니다.

English:
The most important object in this project is `TrendItem`. The reason is simple. YouTube responses look different, Reddit responses look different, and Google Trends responses look different too. But the later processing and output stages need a common language. `TrendItem` is that common language. If this contract becomes unstable, collectors, outputs, and future tools all become unstable with it.

## 6. 처음 실행할 때 실제로 무슨 일이 일어나는가 / What Actually Happens On The First Run

한국어:
`trend-radar run --once`를 실행하면 내부에서는 아래 일이 벌어집니다.

1. 기본 설정 로드
2. `config.yaml` 병합
3. 활성 수집기 판별
4. 각 수집기 실행
5. 결과를 `TrendItem`으로 정규화
6. 플랫폼별 Markdown/JSON 기록
7. `index.json` 생성
8. `daily digest` 생성
9. `run-state.json` 기록

이 흐름을 머릿속에 넣고 있으면, 나중에 버그를 볼 때 “어느 단계에서 망가졌는지”를 훨씬 빨리 짚을 수 있습니다.

English:
When you run `trend-radar run --once`, this is what happens internally.

1. Built-in defaults are loaded.
2. `config.yaml` is merged in.
3. Enabled collectors are selected.
4. Each collector runs.
5. Results are normalized into `TrendItem`.
6. Per-platform Markdown and JSON files are written.
7. `index.json` is generated.
8. A daily digest is generated.
9. `run-state.json` is recorded.

If you keep this flow in your head, debugging gets much easier because you can quickly ask which stage failed.

## 7. 어떤 명령부터 익히면 좋은가 / Which Commands To Learn First

한국어:
처음부터 모든 명령을 외울 필요는 없습니다. 아래 다섯 개면 충분합니다.

- `doctor`: 환경 점검
- `init`: 설정 파일 생성
- `run --once`: 실제 수집
- `status`: 최근 실행 상태 확인
- `digest today`: 오늘 결과 읽기

신입 분들에게는 항상 이렇게 설명합니다. “먼저 시스템이 준비됐는지 확인하고, 그 다음 실행하고, 마지막에 결과를 읽어라.” 그 순서를 습관으로 만들면 대부분의 혼란이 줄어듭니다.

English:
You do not need to memorize every command up front. These five are enough.

- `doctor`: check the environment
- `init`: create configuration
- `run --once`: perform a real collection run
- `status`: inspect the latest run state
- `digest today`: read today’s result

This is how I would explain it to a new teammate: first check whether the system is ready, then run it, then read the result. That order prevents a lot of confusion.

## 8. 결과 파일은 누가 어떻게 쓰는가 / Who Uses Which Output Files

한국어:
결과 파일은 크게 두 부류를 위해 존재합니다.

- 사람
  `*.md` 파일을 읽습니다.
- 다른 도구
  `index.json`이나 플랫폼별 `*.json` 파일을 읽습니다.

여기서 자주 나오는 질문은 “왜 데이터베이스를 안 쓰나요?”입니다. 좋은 질문입니다. 하지만 지금 단계에서는 데이터베이스보다 파일이 더 맞습니다. 공개 배포 초기에는 설치 난이도와 가시성이 더 중요합니다. 파일은 열어보기가 쉽고, 백업도 쉽고, 다른 도구에 넘기기도 쉽습니다.

English:
The output files exist for two broad audiences.

- Humans
  They read the `*.md` files.
- Other tools
  They read `index.json` or the per-platform `*.json` files.

A common question is, “Why not use a database?” That is a fair question. But at this stage, files are the better fit. Early public releases benefit more from easy installation and visibility. Files are easy to inspect, easy to back up, and easy to hand off to other tools.

## 9. 지금 구현된 것과 아직 남은 것 / What Is Already Built And What Still Comes Later

한국어:
이미 구현된 것:

- 공개 소스 실수집
- 설정 스키마
- CLI 기본 명령
- Markdown/JSON 출력
- daily digest
- 환경 점검용 `doctor`
- 테스트와 CI

아직 뒤로 미룬 것:

- Whisper 전사
- 고급 키워드 추출
- 정교한 점수화
- daemon 장기 실행
- TikTok, Instagram, X/Twitter

이 구분을 분명히 두는 이유는, 사용자가 이 저장소를 “완성품”으로 오해하지 않게 하기 위해서입니다. 하지만 동시에 “기반이 없는 아이디어”도 아닙니다. 이미 실제 데이터를 모으고 있기 때문입니다.

English:
Already built:

- Real collection from public sources
- Config schema
- Core CLI commands
- Markdown and JSON outputs
- Daily digest
- `doctor` for environment checks
- Tests and CI

Deferred for later:

- Whisper transcription
- More advanced keyword extraction
- More sophisticated scoring
- Long-running daemon mode
- TikTok, Instagram, X/Twitter

This distinction matters because we do not want users to mistake the repository for a finished all-in-one platform. But it is also not just an idea without implementation. It already collects real data.

## 10. 공개 저장소를 보는 사람에게 꼭 전하고 싶은 말 / The One Message I Want Public Readers To Keep

한국어:
이 프로젝트는 “더 많이 긁는 도구”가 아니라 “다음 작업을 위해 신호를 남겨 두는 도구”입니다. 이 차이를 이해하면, 왜 파일 구조가 중요한지, 왜 `index.json` 계약이 중요한지, 왜 `doctor` 같은 작은 명령이 중요한지 자연스럽게 이해됩니다.

English:
This project is not mainly a tool for scraping more. It is a tool for preserving signal for the next step of work. Once you understand that distinction, the file structure, the `index.json` contract, and even small commands like `doctor` start to make sense.

마지막으로 한 문장만 남기겠습니다. 좋은 자동화는 사람을 지우는 자동화가 아니라, 사람의 판단이 더 늦지 않게 도와주는 자동화입니다.

One closing sentence. Good automation does not remove human judgment. It keeps judgment from arriving too late.
