# trend-radar n8n Integration

왜 이 문서가 먼저 있느냐부터 말씀드리겠습니다.  
많은 자동화가 실패하는 이유는 n8n이 부족해서가 아니라, 원래 있던 CLI와 새 워크플로우 사이의 인수인계가 흐릿하기 때문입니다. `trend-radar`는 이미 수집기와 출력 계약이 분리된 프로젝트이기 때문에 n8n을 붙이기 좋은 편입니다. 반대로 말하면, 워크플로우를 아무렇게나 붙이면 장점이 바로 사라집니다. 이 가이드는 그 손실을 막기 위해 존재합니다.

English: Here is the real reason this guide exists. Most automations fail not because n8n is weak, but because the handoff between an existing CLI and a new workflow gets fuzzy. `trend-radar` is a good fit for n8n because collection and output contracts are already separated. The downside is that careless wiring can erase that advantage quickly. This guide exists to prevent that loss.

Meta description: Korean-first bilingual guide for connecting trend-radar to self-hosted n8n with webhook, schedule, and digest workflows.

Labels: n8n, automation, trend-radar, cli, webhook, schedule, 22b-labs

Author: 22B Labs · The 4th Path | GitHub: `sinmb79`

## 무엇이 들어 있나 / What Is Included

- `workflow.json`
  한국어: 수동 실행, 웹훅 실행, 예약 실행을 하나로 묶은 기본 수집 워크플로우입니다.
  English: The main collection workflow combining manual, webhook, and scheduled runs.
- `workflow-digest.json`
  한국어: 일일 digest 생성에 집중한 보조 워크플로우입니다.
  English: A companion workflow focused on daily digest generation.

## 먼저 알아둘 점 / One Important Truth First

이 연동은 “n8n이 trend-radar를 대신 실행한다”가 아닙니다.  
정확히는 “n8n이 trend-radar CLI를 안전하게 호출하고, 그 결과를 다음 자동화로 넘긴다”가 맞습니다.

English: This integration does not mean “n8n replaces trend-radar.” The correct framing is: “n8n safely calls the trend-radar CLI and passes the result into downstream automation.”

이 차이가 중요한 이유는 유지보수 때문입니다. CLI가 진실의 원천이면, 디버깅은 한 군데에서 하고 자동화는 여러 군데로 늘릴 수 있습니다. 반대로 n8n 안에 비즈니스 로직이 너무 많이 들어가면, 보기에는 쉬워도 나중에는 더 비싸집니다.

English: This distinction matters for maintenance. If the CLI remains the source of truth, debugging stays centralized while automation can grow outward. If too much business logic moves into n8n, the workflow may look easier today but become more expensive later.

## 사전 준비 / Prerequisites

- `n8n`은 반드시 self-hosted 버전이어야 합니다.
  English: n8n must be self-hosted.
- `Execute Command` 노드가 필요합니다. 그래서 n8n Cloud에는 이 워크플로우를 그대로 쓸 수 없습니다.
  English: These workflows rely on the `Execute Command` node, so they don't work as-is on n8n Cloud.
- `trend-radar`는 n8n이 돌아가는 같은 환경에서 실행 가능해야 합니다.
  English: `trend-radar` must be runnable from the same environment where n8n is running.
- 아래 둘 중 하나는 미리 끝내 두는 것을 권장합니다.
  English: Finish one of these installation paths first.

```bash
poetry install
poetry run trend-radar doctor
```

```bash
python -m pip install --user --no-cache-dir -e .
python -m trend_radar doctor
```

카운터인튜이티브한 포인트가 하나 있습니다. 보통 사람들은 n8n import부터 하려 하지만, 실제로는 `doctor`가 먼저입니다. 자동화 문제처럼 보이는 것의 절반은 환경 문제이기 때문입니다.

English: Here is the counterintuitive part. Most people want to import the workflow first, but `doctor` should come first. A surprising amount of “automation problems” are really environment problems.

## 워크플로우 1: 수집 실행 / Workflow 1: Collection Run

`workflow.json`은 세 가지 시작점을 갖습니다.

English: `workflow.json` has three entry points.

1. `Manual Trigger`
   한국어: n8n 화면에서 바로 테스트할 때 씁니다.
   English: Use this when testing directly inside the n8n editor.
2. `Webhook Trigger`
   한국어: 외부 서비스나 다른 시스템이 HTTP로 수집을 요청할 때 씁니다.
   English: Use this when another system wants to trigger collection over HTTP.
3. `Schedule Trigger`
   한국어: 워크플로우를 활성화했을 때 매 1시간마다 자동 실행합니다.
   English: Runs every hour after you activate the workflow.

실행 흐름은 단순합니다.

English: The execution flow is intentionally simple.

1. 입력값을 정리합니다.
   English: Normalize incoming values.
2. `trend-radar run --once --json` 명령을 만듭니다.
   English: Build a `trend-radar run --once --json` command.
3. 로컬에서 CLI를 실행합니다.
   English: Execute the CLI on the local machine.
4. stdout JSON을 파싱해 다음 노드가 읽기 쉬운 형태로 넘깁니다.
   English: Parse the CLI JSON output into a workflow-friendly result.

## 워크플로우 2: 일일 digest / Workflow 2: Daily Digest

`workflow-digest.json`은 digest 생성만 담당합니다.

English: `workflow-digest.json` focuses only on digest generation.

1. `Manual Trigger`로 즉시 실행할 수 있습니다.
   English: You can run it immediately with the manual trigger.
2. `Schedule Trigger`는 기본값으로 매일 22:00에 돌게 되어 있습니다.
   English: The schedule trigger is set to run daily at 22:00 by default.
3. 내부적으로 `trend-radar digest today --json`을 호출합니다.
   English: Internally it calls `trend-radar digest today --json`.
4. 결과에서 `path`, `content`, `preview`를 꺼내 다음 알림 노드에 붙이기 쉽게 만듭니다.
   English: It surfaces `path`, `content`, and `preview` so the result is easy to pass to a notification node.

## import 방법 / How To Import

1. n8n에서 **Import from File**을 엽니다.
   English: In n8n, open **Import from File**.
2. [workflow.json](./workflow.json) 또는 [workflow-digest.json](./workflow-digest.json)을 불러옵니다.
   English: Import [workflow.json](./workflow.json) or [workflow-digest.json](./workflow-digest.json).
3. `Normalize Inputs` 또는 `Prepare Digest Command` 노드를 엽니다.
   English: Open the `Normalize Inputs` or `Prepare Digest Command` node.
4. 기본 경로와 실행 런처가 자기 환경과 맞는지 확인합니다.
   English: Check that the default path and launcher match your environment.
5. 먼저 `Manual Trigger`로 한 번 돌립니다.
   English: Run it once through the manual trigger first.

## 가장 먼저 수정할 값 / The First Values To Edit

현재 워크플로우 기본값은 22B Labs의 Windows 기준값입니다.

English: The shipped defaults target the 22B Labs Windows environment.

- `project_dir`
  한국어: 기본값은 `D:\workspace\trend-radar`입니다.
  English: Defaults to `D:\workspace\trend-radar`.
- `launcher`
  한국어: 기본값은 `python -m trend_radar`입니다.
  English: Defaults to `python -m trend_radar`.
- `output_dir`
  한국어: 비워 두면 CLI 기본값 또는 `config.yaml` 값을 그대로 씁니다.
  English: Leave it empty to use the CLI default or the value from `config.yaml`.
- `config_path`
  한국어: 비워 두면 기본 설정 또는 현재 작업 디렉터리의 설정을 씁니다.
  English: Leave it empty to use the default config resolution behavior.
- `source`
  한국어: 비워 두면 활성 수집기를 모두 돌리고, 값을 넣으면 한 소스만 실행합니다.
  English: Leave it empty to run all enabled collectors, or set it to run a single source.

## Linux 또는 macOS에서 쓸 때 / If You Run This On Linux Or macOS

이 워크플로우는 Windows 기본 셸을 기준으로 `cd /d`를 사용합니다. Linux나 macOS에서는 `Normalize Inputs` 또는 `Prepare Digest Command` 노드에서 아래처럼 바꾸면 됩니다.

English: The bundled workflow uses `cd /d` because the reference environment is Windows. On Linux or macOS, edit the command template inside `Normalize Inputs` or `Prepare Digest Command` to the form below.

```bash
cd /path/to/trend-radar && python -m trend_radar run --once --json
```

```bash
cd /path/to/trend-radar && python -m trend_radar digest today --json
```

여기서 핵심은 운영체제보다도 “n8n 프로세스가 그 명령을 실제로 실행할 수 있느냐”입니다. Docker 안의 n8n이면, 호스트 경로가 아니라 컨테이너 내부 경로로 바꿔야 합니다.

English: The real issue is less the OS and more whether the n8n process can actually reach the command. If n8n runs inside Docker, you must use container paths, not host paths.

## 웹훅 입력 예시 / Example Webhook Payload

아래 값들은 모두 선택값입니다. 기본값이 자기 머신과 다를 때만 보내면 됩니다.

English: All of these fields are optional. Send only the ones that differ from the workflow defaults.

```json
{
  "project_dir": "D:\\workspace\\trend-radar",
  "launcher": "python -m trend_radar",
  "output_dir": "D:\\trend-radar-data",
  "source": "youtube",
  "config_path": "D:\\workspace\\trend-radar\\config.yaml"
}
```

## CLI가 돌려주는 JSON / JSON Returned By The CLI

이 패치부터 `trend-radar`는 자동화를 위해 `--json` 출력을 지원합니다.

English: Starting with this patch, `trend-radar` supports `--json` output for automation.

수집 워크플로우는 대략 이런 구조를 받습니다.

English: The collection workflow receives a payload like this.

```json
{
  "status": "ok",
  "output_dir": "D:\\trend-radar-data",
  "total_items": 75,
  "index_path": "D:\\trend-radar-data\\index.json",
  "digest_path": "D:\\trend-radar-data\\digest\\daily-2026-04-02.md",
  "warnings": [],
  "errors": [],
  "collectors": {
    "youtube": {
      "name": "youtube",
      "item_count": 20,
      "warnings": [],
      "errors": [],
      "skipped": false
    }
  }
}
```

이 구조를 쓰면 Telegram, Slack, Notion, Google Sheets 같은 다음 노드를 붙일 때 훨씬 단순해집니다.

English: This structure makes it much easier to attach downstream nodes such as Telegram, Slack, Notion, or Google Sheets.

## 보안 주의사항 / Security Notes

가장 중요한 경고를 먼저 드리겠습니다. `Webhook Trigger`는 import 직후 바로 테스트되도록 인증을 끈 상태입니다. 이건 편의를 위한 기본값이지, 공개 인터넷에 그대로 노출하라는 뜻이 아닙니다.

English: Here is the most important warning. The `Webhook Trigger` ships with authentication disabled so you can test it immediately after import. That is a convenience default, not a recommendation for public exposure.

- 외부 공개 전에 `Header Auth` 또는 `JWT Auth`를 설정하세요.
  English: Set `Header Auth` or `JWT Auth` before exposing the webhook externally.
- 가능하면 IP allowlist도 같이 사용하세요.
  English: Add an IP allowlist if possible.
- `Execute Command`가 로컬 명령을 실행한다는 사실을 잊지 마세요.
  English: Remember that `Execute Command` runs local shell commands.

편리한 자동화와 안전한 자동화는 같은 것이 아닙니다. 둘을 구분하는 습관이 운영 비용을 크게 줄입니다.

English: Convenient automation and safe automation are not the same thing. Keeping them separate saves real operational cost.

## 다음으로 붙이기 좋은 노드 / Good Next Nodes To Add

- Telegram
  한국어: `Parse Run Report` 또는 `Parse Digest Result` 뒤에 붙여 요약 메시지를 보낼 수 있습니다.
  English: Attach it after `Parse Run Report` or `Parse Digest Result` to send summaries.
- Slack
  한국어: 팀 채널 리포트에 잘 맞습니다.
  English: Good for team reporting channels.
- Google Sheets
  한국어: 키워드 추세를 가볍게 누적 기록할 때 편합니다.
  English: Handy for lightweight keyword trend logging.
- HTTP Request
  한국어: 다른 22B Labs 시스템으로 `index.json` 경로와 메타데이터를 넘길 수 있습니다.
  English: Use it to forward `index.json` paths and metadata to other 22B Labs systems.

일부러 Telegram 노드를 기본 워크플로우에 강제로 넣지 않았습니다. 이유는 단순합니다. import 직후부터 자격증명 오류에 막히면, 초보자는 워크플로우보다 자기 자신을 먼저 의심하게 되기 때문입니다.

English: Telegram nodes were intentionally not baked into the default workflows. The reason is simple: if the first experience is a credential error, beginners tend to doubt themselves before they understand the workflow.

## 마지막 조언 / Final Advice

좋은 n8n 연동은 노드를 많이 붙이는 데서 나오지 않습니다. 이미 믿을 수 있는 CLI를 덜 흔들리게 연결하는 데서 나옵니다.

English: Good n8n integration does not come from adding more nodes. It comes from connecting an already trustworthy CLI with less friction and less ambiguity.

신호를 더 빨리 모으는 것보다, 신호가 도중에 사라지지 않게 만드는 편이 더 강합니다.
