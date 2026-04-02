# trend-radar 시작하기

## 왜 이 프로젝트가 존재하나

`trend-radar`는 트렌드를 모으는 일과 실제로 쓰는 일 사이의 단절을 줄이기 위해 만들어졌습니다. 수집된 신호를 로컬 파일로 남겨서 사람과 도구가 같은 결과물을 함께 읽을 수 있게 합니다.

## 설치

```bash
poetry install
```

Poetry가 아직 없다면:

```bash
python -m pip install --user --no-cache-dir -e .
```

## 첫 실행

1. 환경 점검
   `poetry run trend-radar doctor`
2. 설정 파일 생성
   `poetry run trend-radar init`
3. 1회 수집 실행
   `poetry run trend-radar run --once`
4. 오늘의 다이제스트 확인
   `poetry run trend-radar digest today`

## 기본 데이터 소스

- YouTube
- Reddit
- Google Trends
- Generic RSS

`Naver DataLab`은 지원하지만 `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`가 있어야 활성화됩니다.

## 출력 파일

- `feeds/<platform>/<YYYY-MM-DD>.json`
- `feeds/<platform>/<YYYY-MM-DD>.md`
- `digest/daily-<YYYY-MM-DD>.md`
- `index.json`
- `run-state.json`

## 공개배포 기준

- 라이선스: MIT
- Python: 3.11+
- 상태: alpha
- 현재 수집 방식: one-shot CLI
- 장기 실행 daemon 모드: 후속 단계로 보류
