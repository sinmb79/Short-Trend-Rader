# trend-radar v0.2.1 Release Notes

왜 이 패치 릴리즈가 필요한지부터 말씀드리겠습니다.  
`v0.2.0`이 `trend-radar`를 n8n과 연결 가능한 시스템으로 바꿨다면, `v0.2.1`은 그 연결을 “실제로 처음 쓰는 사람도 바로 켤 수 있는 상태”로 밀어 올리는 릴리즈입니다. 자동화는 기능이 아니라 진입장벽과의 싸움이기도 한데, 이번 패치는 그 입구를 낮추는 데 집중했습니다.

English: Let’s start with why this patch release exists. If `v0.2.0` turned `trend-radar` into a system that could connect to n8n, `v0.2.1` turns that connection into something a first-time user can actually start without handholding. Automation is not only about features. It is also a fight against setup friction. This patch is focused on lowering that entrance cost.

Meta description: trend-radar v0.2.1 adds one-click setup scripts for n8n install, startup, and workflow import.

Labels: trend-radar, release, n8n, setup, automation, python, 22b-labs

Author: 22B Labs · The 4th Path | GitHub: `sinmb79`

## 한 줄 요약 / One-Line Summary

`v0.2.1`은 `setup.sh`와 `setup.bat`를 추가해 n8n 설치, 실행, 워크플로우 임포트까지 한 번에 처리하는 패치 릴리즈입니다.  
English: `v0.2.1` is a patch release that adds `setup.sh` and `setup.bat` so n8n installation, startup, and workflow import can happen in one flow.

## 무엇이 달라졌나 / What Changed

### 1. 원클릭 설치 스크립트 / One-Click Setup Scripts

- [setup.sh](https://github.com/sinmb79/Short-Trend-Rader/blob/main/setup.sh)
  한국어: Linux와 macOS용 설치 스크립트입니다.
  English: Setup script for Linux and macOS.
- [setup.bat](https://github.com/sinmb79/Short-Trend-Rader/blob/main/setup.bat)
  한국어: Windows용 설치 스크립트입니다.
  English: Setup script for Windows.

이 스크립트들은 단순히 패키지만 설치하지 않습니다. 현재 클론된 경로를 기준으로 n8n 워크플로우의 `project_dir` 기본값을 맞춰 패치하고, n8n을 실행한 뒤, 워크플로우를 바로 임포트합니다.

English: These scripts do more than install a package. They patch the n8n workflows so the default `project_dir` matches the current clone path, start n8n, and import the workflows automatically.

### 2. README 설치 흐름 단순화 / Simplified Install Flow In README

- [README.md](https://github.com/sinmb79/Short-Trend-Rader/blob/main/README.md)
  한국어: 설치 섹션을 “3단계면 끝” 흐름으로 다시 썼습니다.
  English: The install section was rewritten as a simple “3-step and done” path.

좋은 README는 모든 걸 설명하는 문서가 아니라, 처음 30초를 성공시키는 문서입니다. 이번 변경은 그 철학에 더 가깝게 다듬은 것입니다.

English: A good README is not the one that explains everything. It is the one that gets the first 30 seconds right. This update pushes the repository closer to that standard.

### 3. 릴리즈 버전 정합성 / Version Consistency

- Python 패키지 버전이 `0.2.1`로 올라갔습니다.
  English: The Python package version now moves to `0.2.1`.
- `index.json`에 기록되는 버전 문자열도 `0.2.1`로 맞췄습니다.
  English: The version string recorded in `index.json` is now `0.2.1` as well.

## 실제로 어떻게 쓰나 / How You Use It

가장 쉬운 시작 경로는 아래와 같습니다.  
English: The easiest starting path now looks like this.

```bash
git clone https://github.com/sinmb79/Short-Trend-Rader.git
cd Short-Trend-Rader

# Linux / macOS
chmod +x setup.sh
./setup.sh

# Windows
setup.bat
```

실행이 끝나면 브라우저에서 `http://localhost:5678`을 열면 됩니다.  
English: When the script finishes, open `http://localhost:5678` in your browser.

목록에는 `trend-radar Collection Orchestrator`와 `trend-radar Daily Digest`가 보여야 합니다.  
English: You should see `trend-radar Collection Orchestrator` and `trend-radar Daily Digest` in the workflow list.

## 왜 이게 생각보다 중요한가 / Why This Matters More Than It Looks

많은 자동화 프로젝트가 기능은 잘 만들어 놓고도 첫 설치에서 사람을 잃습니다. 환경을 맞추고, 경로를 바꾸고, n8n을 띄우고, 워크플로우를 손으로 import하는 과정에서 초보자는 시스템보다 자기 자신을 먼저 의심하게 됩니다. 이번 패치는 바로 그 지점을 줄입니다.

English: Many automation projects lose people not in the feature layer but in the first setup. By the time a beginner has aligned the environment, changed paths, started n8n, and imported workflows by hand, they often doubt themselves before they understand the system. This patch is aimed directly at that failure point.

여기서 역설적인 사실이 하나 있습니다. 성숙한 자동화는 보통 복잡한 노드에서 시작하지 않습니다. 오히려 가장 단순한 설치 경험에서 시작합니다.

English: There is a counterintuitive truth here. Mature automation rarely begins with complex workflows. It usually begins with the simplest possible setup experience.

## 검증 상태 / Verification Status

- `python -m pytest` 통과
  English: `python -m pytest` passes.
- 버전 문자열 `0.2.1` 반영 확인
  English: Confirmed version strings are updated to `0.2.1`.
- Windows 배치 스크립트 정적 점검 완료
  English: Completed static review of the Windows batch script.
- 현재 환경에 WSL `bash`가 없어 `setup.sh` 문법 검사는 별도로 실행하지 못함
  English: This environment does not have WSL `bash`, so `setup.sh` syntax was reviewed manually rather than executed through `bash -n`.

## 마무리 / Closing

`v0.2.1`은 기능을 더 크게 만든 릴리즈가 아니라, 첫 실행의 망설임을 줄인 릴리즈입니다.  
English: `v0.2.1` is not the release that makes the feature set bigger. It is the release that reduces hesitation on the first run.

좋은 자동화는 똑똑한 기능보다 먼저, 덜 헤매는 시작을 제공합니다.
