# trend-radar v0.2.0 Release Notes

왜 이 릴리즈가 필요한지부터 말씀드리겠습니다.  
이 프로젝트는 이미 데이터를 수집할 수 있었지만, 팀 자동화와 외부 워크플로우가 안전하게 붙을 수 있는 “연결 표면”은 아직 얇았습니다. 사람은 Markdown을 읽고, 도구는 JSON을 읽는다는 원칙은 있었지만, 정작 자동화 오케스트레이션 계층까지는 다리가 놓여 있지 않았습니다. 이번 `v0.2.0`은 그 다리를 놓는 릴리즈입니다.

English: Let’s start with why this release exists. The project could already collect data, but the connection surface for team automation and external workflows was still thin. We had the principle that humans read Markdown and tools read JSON, but there was no real bridge into an orchestration layer. `v0.2.0` is the release that builds that bridge.

Meta description: trend-radar v0.2.0 adds n8n workflows, machine-readable CLI output, and release-grade automation docs.

Labels: trend-radar, release, n8n, automation, cli, python, 22b-labs

Author: 22B Labs · The 4th Path | GitHub: `sinmb79`

## 한 줄 요약 / One-Line Summary

`v0.2.0`은 `trend-radar`를 “잘 돌아가는 로컬 수집기”에서 “다른 시스템이 바로 연결할 수 있는 공개용 자동화 기반”으로 끌어올리는 릴리즈입니다.  
English: `v0.2.0` turns `trend-radar` from a working local collector into a public automation foundation that other systems can connect to immediately.

## 무엇이 새로 들어갔나 / What’s New

### 1. n8n 연동 자산 추가 / New n8n Integration Assets

이번 릴리즈의 중심은 `n8n/` 디렉터리입니다.  
English: The center of this release is the new `n8n/` directory.

- [workflow.json](../n8n/workflow.json)
  한국어: 수동 실행, 웹훅 실행, 예약 실행을 묶은 기본 수집 워크플로우입니다.
  English: The main workflow for manual runs, webhook runs, and scheduled runs.
- [workflow-digest.json](../n8n/workflow-digest.json)
  한국어: 일일 digest 생성 전용 워크플로우입니다.
  English: A focused workflow for daily digest generation.
- [n8n/README.md](../n8n/README.md)
  한국어: 설정, import, 보안 주의사항, Linux/macOS 차이까지 설명한 한국어 우선 가이드입니다.
  English: A Korean-first guide covering setup, import, security notes, and Linux/macOS differences.

많은 프로젝트가 자동화를 붙일 때 제일 먼저 복잡한 비주얼 흐름부터 만듭니다. 하지만 오래가는 자동화는 노드 수가 아니라 계약의 선명도에서 나옵니다. 이번 릴리즈는 그 점을 의식해서, 화려함보다 재현성과 설명 가능성을 우선했습니다.

English: Many projects jump straight into complex visual workflows when they add automation. Long-lived automation, however, depends less on node count and more on contract clarity. This release prioritizes reproducibility and explainability over visual complexity.

### 2. CLI의 기계 친화적 출력 / Machine-Friendly CLI Output

이제 아래 명령들은 `--json` 출력을 지원합니다.  
English: The following commands now support `--json` output.

- `trend-radar run --once --json`
- `trend-radar status --json`
- `trend-radar doctor --json`
- `trend-radar digest today --json`
- `trend-radar config show --json`

이 변화는 작아 보여도 매우 중요합니다. n8n이 텍스트를 읽고 정규식으로 의미를 추측하는 구조는 데모에서는 빨라 보여도, 운영에 가까워질수록 취약해집니다. 구조화된 출력은 자동화의 사치를 줄이고, 실패 원인을 추적하기 쉽게 만듭니다.

English: This may look small, but it is a major shift. A workflow that reads text and guesses meaning with regex can feel fast in a demo, but it becomes fragile as you move closer to production. Structured output lowers automation friction and makes failures easier to trace.

### 3. 공개 릴리즈 관점의 문서 보강 / Release-Grade Documentation

이번 릴리즈에서 문서는 부록이 아니라 기능의 일부입니다.  
English: In this release, documentation is not an appendix. It is part of the feature.

- [README.md](../README.md)
  한국어: n8n 연동 개요를 추가했습니다.
  English: Now includes an n8n integration overview.
- [docs/system-guide-ko-en.md](./system-guide-ko-en.md)
  한국어: 전체 구조와 역할 설명을 계속 유지합니다.
  English: Continues to provide the broader system explanation.
- [docs/release-notes-v0.2.0-ko-en.md](./release-notes-v0.2.0-ko-en.md)
  한국어: 지금 읽고 있는 이 릴리즈 설명문입니다.
  English: This is the release document you are reading now.

## 실제로 어떻게 쓰나 / How You Actually Use It

가장 쉬운 시작 방법은 아래 순서입니다.  
English: The easiest starting path is the following sequence.

1. `trend-radar doctor`로 환경을 확인합니다.
   English: Check the environment with `trend-radar doctor`.
2. `trend-radar run --once`로 실제 수집을 확인합니다.
   English: Confirm collection with `trend-radar run --once`.
3. n8n에서 [workflow.json](../n8n/workflow.json)을 import합니다.
   English: Import [workflow.json](../n8n/workflow.json) into n8n.
4. `project_dir`와 `launcher`를 자기 환경에 맞게 바꿉니다.
   English: Adjust `project_dir` and `launcher` to match your environment.
5. `Manual Trigger`로 먼저 성공을 확인한 뒤, 필요하면 `Webhook`과 `Schedule`로 확장합니다.
   English: Validate with `Manual Trigger` first, then expand to `Webhook` and `Schedule` if needed.

여기서 의외로 중요한 점은 “바로 자동화하지 않는 용기”입니다. 많은 시스템이 스케줄부터 걸고 나서 나중에 로그를 뒤쫓습니다. 하지만 먼저 수동 경로가 깨끗하게 성공해야 나중에 스케줄도 믿을 수 있습니다.

English: The counterintuitive discipline here is resisting the urge to automate immediately. Many systems start with schedules and only later chase logs. In practice, you trust the schedule only after the manual path succeeds cleanly.

## 호환성과 변경 영향 / Compatibility and Change Impact

이번 릴리즈는 기능 추가 중심입니다.  
English: This release is primarily additive.

- 기존 `run --once`, `status`, `digest today`, `doctor` 사용 방식은 유지됩니다.
  English: Existing usage of `run --once`, `status`, `digest today`, and `doctor` remains intact.
- `--json`은 선택 옵션이므로 기존 사람이 읽는 출력은 그대로 남아 있습니다.
  English: `--json` is optional, so human-readable output remains unchanged.
- `index.json` 버전 문자열은 `0.2.0`으로 올라갑니다.
  English: The `index.json` version string now moves to `0.2.0`.

즉, 이번 릴리즈는 “기존 흐름을 깨고 새 방식을 강요하는 변경”이 아니라, “기존 흐름 위에 자동화용 표면을 겹쳐 놓는 변경”에 가깝습니다.

English: In other words, this is not a release that breaks the old path and forces a new one. It overlays an automation-ready surface on top of the existing path.

## 검증 상태 / Verification Status

이번 릴리즈는 아래 기준으로 검증했습니다.  
English: This release was verified against the following checks.

- `python -m pytest` 통과
  English: `python -m pytest` passes.
- `python -m trend_radar status --json` 확인
  English: Verified `python -m trend_radar status --json`.
- `python -m trend_radar doctor --json` 확인
  English: Verified `python -m trend_radar doctor --json`.
- `python -m trend_radar run --once --json` 실제 수집 성공
  English: Confirmed a successful live collection with `python -m trend_radar run --once --json`.
- n8n 워크플로우 구조 검증 통과
  English: Both n8n workflows passed structural validation.

## 알려진 한계 / Known Limits

정직하게 말하면, 이번 릴리즈가 모든 자동화 문제를 끝내지는 않습니다.  
English: To be honest, this release does not solve every automation problem.

- `Execute Command` 기반이므로 self-hosted n8n이 전제입니다.
  English: Because it relies on `Execute Command`, self-hosted n8n is required.
- Windows 기준 기본 경로가 포함되어 있어 Linux/macOS에서는 명령 템플릿을 조금 수정해야 합니다.
  English: The shipped defaults assume Windows, so Linux/macOS users need to adjust the command template.
- 키워드 품질과 digest 고도화는 다음 단계에서 더 다듬을 수 있습니다.
  English: Keyword quality and digest sophistication can be improved further in the next phase.

그렇지만 중요한 것은 완벽함이 아니라 방향입니다. 이번 릴리즈는 일단 수집 시스템을 “연결 가능한 시스템”으로 바꿨고, 그 다음부터는 정교함을 쌓아 올릴 수 있습니다.

English: What matters here is not perfection but direction. This release turns the collector into a connectable system, and that makes later refinement much more valuable.

## 마무리 / Closing

`v0.2.0`은 기능이 하나 더 늘어난 버전이 아니라, `trend-radar`가 다른 도구들과 같은 문장으로 대화하기 시작한 첫 버전입니다.  
English: `v0.2.0` is not just a version with one more feature. It is the first version where `trend-radar` begins to speak the same language as other tools.

좋은 수집기는 많이 모으는 도구가 아니라, 연결해도 흐트러지지 않는 도구입니다.
