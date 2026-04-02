# trend-radar Masterplan

**Codename: "Radar"**
**Repo: sinmb79/trend-radar**
**Author: 22B Labs (the4thpath.com)**
**Date: 2026-04-02**
**Status: DRAFT — Pending Boss Review**

---

## 1. Executive Summary

trend-radar is 22B Labs' **universal trend intelligence daemon** — a 24/7 background service that continuously collects, transcribes, and digests trending content from multiple platforms, outputting structured MD/JSON files that any 22B Labs tool (or user) can consume.

### One-Line Pitch

> "자는 동안 트렌드를 잡아주는 개인 리서치 팀"

### Core Identity

```
trend-radar ≠ scraper (단순 수집기)
trend-radar = intelligence layer (수집 → 전사 → 분석 → 요약 → 배포)
```

### Consumers

| Consumer | Usage |
|----------|-------|
| **Shorts-engine** | `--trend-aware` 플래그로 시나리오에 트렌드 반영 |
| **blog-writer** | 트렌드 키워드 → 블로그 주제 자동 추천 |
| **MediaForge** | 인기 포맷/스타일 패턴 → 영상 템플릿 반영 |
| **사용자 직접** | daily digest MD 읽기, 키워드 모니터링 |

---

## 2. Design Philosophy

### 22B Labs Principles Applied

1. **Base Free, Fully Working**: 무료 소스만으로 100% 작동 (YouTube RSS, Google Trends, Reddit RSS, Naver DataLab)
2. **User Choice for Everything Else**: 유료 API(TikTok scraping 등)는 선택적 플러그인
3. **Offline-First Output**: 모든 결과물은 로컬 MD/JSON 파일 — 클라우드 의존 없음
4. **MIT License**

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Python (not TypeScript) | Whisper, Playwright, NLP 생태계 최적 |
| Daemon mode + CLI mode | 미니PC 24/7 상시 + 수동 1회 실행 모두 지원 |
| Plugin architecture | 플랫폼 추가/제거가 코어에 영향 없음 |
| MD + JSON dual output | 사람(MD) + 기계(JSON) 모두 소비 가능 |

---

## 3. Architecture

### 3.1 System Overview

```
┌──────────────────────────────────────────────────────────────┐
│                        trend-radar                            │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  Collectors  │→│  Processors  │→│     Outputs           │ │
│  │             │  │              │  │                      │ │
│  │ • TikTok    │  │ • Transcribe │  │ • feeds/*.md         │ │
│  │ • YouTube   │  │   (Whisper)  │  │ • keywords/*.md      │ │
│  │ • Instagram │  │ • Translate  │  │ • digest/daily.md    │ │
│  │ • X/Twitter │  │ • Extract    │  │ • digest/weekly.md   │ │
│  │ • Reddit    │  │   Keywords   │  │ • index.json         │ │
│  │ • Naver     │  │ • Classify   │  │ • alerts/*.md        │ │
│  │ • Google    │  │ • Score      │  │                      │ │
│  │   Trends    │  │ • Summarize  │  │                      │ │
│  └─────────────┘  └──────────────┘  └──────────────────────┘ │
│                                                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    Scheduler                              │ │
│  │  cron / daemon mode / one-shot CLI                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                User Config (config.yaml)                  │ │
│  │  channels, keywords, categories, schedule, language       │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 Directory Structure

```
trend-radar/
  src/
    cli.py                    # CLI entry point
    daemon.py                 # 24/7 daemon mode
    scheduler.py              # Cron-like scheduler

    collectors/               # Platform plugins
      base.py                 # Abstract collector interface
      tiktok.py               # TikTok trending (Playwright + cookies)
      youtube.py              # YouTube Explore (RSS + yt-dlp metadata)
      instagram.py            # Instagram Reels (Playwright)
      x_twitter.py            # X/Twitter trending (API v2 free tier)
      reddit.py               # Reddit hot/rising (RSS + PRAW)
      naver.py                # Naver DataLab API + 실시간 검색어
      google_trends.py        # Google Trends API (alpha) + pytrends
      rss_generic.py          # Generic RSS feed collector

    processors/
      transcriber.py          # Whisper (local) / whisper.cpp
      translator.py           # Optional: KO↔EN translation
      keyword_extractor.py    # TF-IDF + KeyBERT (local)
      classifier.py           # Category auto-tagging
      scorer.py               # Trend velocity scoring
      summarizer.py           # LLM summarize (optional) / extractive

    outputs/
      md_writer.py            # Markdown file generator
      json_writer.py          # JSON index generator
      digest_builder.py       # Daily/weekly digest compiler
      alert_engine.py         # Keyword spike alert

    config/
      schema.py               # Config validation
      defaults.py             # Default config values

  config.yaml                 # User configuration
  requirements.txt
  setup.py
  tests/
  docs/
    getting-started-ko.md
    getting-started-en.md
```

### 3.3 Plugin Interface

```python
# collectors/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class TrendItem:
    platform: str               # "tiktok", "youtube", etc.
    item_id: str                # Platform-specific ID
    title: str                  # Video title / post title
    description: str            # Caption / description text
    transcript: Optional[str]   # Whisper-transcribed text (if video)
    url: str                    # Source URL
    author: str                 # Creator name
    metrics: dict               # {"views": N, "likes": N, "shares": N, ...}
    hashtags: List[str]         # Extracted hashtags
    keywords: List[str]         # Auto-extracted keywords
    category: str               # Auto-classified category
    language: str               # Detected language
    trend_score: float          # 0-100 velocity score
    collected_at: str           # ISO timestamp
    media_url: Optional[str]    # Video/image URL (for optional download)

class BaseCollector(ABC):
    @abstractmethod
    async def collect(self, config: dict) -> List[TrendItem]:
        """Collect trending items from platform."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this collector can run (API keys, etc.)."""
        pass
```

---

## 4. Data Sources — Tier System

### Tier 1: Free, No API Key (항상 작동)

| Source | Method | Data | Rate |
|--------|--------|------|------|
| **YouTube** | RSS + yt-dlp metadata | Trending videos, Shorts, metadata | Every 1h |
| **Reddit** | RSS feeds (no auth) | Hot/rising posts from subreddits | Every 1h |
| **Google Trends** | pytrends (unofficial) | Trending searches, related topics | Every 6h |
| **Naver DataLab** | Open API (free tier) | Search trend volumes | Every 6h |
| **Generic RSS** | Any RSS/Atom feed | News, blogs, industry feeds | Per config |

### Tier 2: Free API Key Required

| Source | Method | Data | Requirement |
|--------|--------|------|-------------|
| **X/Twitter** | API v2 free tier | Trending topics, recent tweets | Developer account |
| **Naver Search** | Naver Open API | Blog/cafe/news trends | Client ID/Secret |
| **Google Trends API** | Official alpha API | Trend data (structured) | Alpha access |

### Tier 3: Advanced (Optional, Complexity/Risk)

| Source | Method | Data | Note |
|--------|--------|------|------|
| **TikTok** | Playwright scraping | Trending videos, captions, metadata | TOS risk, anti-bot |
| **Instagram** | Playwright scraping | Reels trending, hashtags | TOS risk, login needed |
| **TikTok API** | Research API (official) | Full metadata, no video | Requires approval |

### Default Config (Tier 1 only — zero setup)

```yaml
collectors:
  youtube:
    enabled: true
    regions: ["KR", "US"]
    categories: ["trending", "shorts"]
  reddit:
    enabled: true
    subreddits: ["popular", "technology", "videos", "TikTok"]
  google_trends:
    enabled: true
    regions: ["KR", "US"]
  naver_datalab:
    enabled: true
  rss:
    enabled: true
    feeds: []
```

---

## 5. User Configuration

### 5.1 config.yaml

```yaml
# trend-radar configuration
# All fields optional — sensible defaults applied

# ── 수집 대상 ──
collectors:
  youtube:
    enabled: true
    regions: ["KR", "US"]
    categories: ["trending", "shorts", "music"]
    max_items: 50

  tiktok:
    enabled: false  # Tier 3, requires setup
    method: "playwright"  # or "api" if approved
    regions: ["KR", "US"]
    max_items: 30

  reddit:
    enabled: true
    subreddits:
      - "popular"
      - "technology"
      - "Cooking"
      - "TikTokCringe"
    sort: "hot"
    max_items: 30

  x_twitter:
    enabled: false  # Requires API key
    api_key_env: "X_BEARER_TOKEN"

  naver_datalab:
    enabled: true
    client_id_env: "NAVER_CLIENT_ID"
    client_secret_env: "NAVER_CLIENT_SECRET"

  google_trends:
    enabled: true
    regions: ["KR", "US"]

  rss:
    enabled: true
    feeds:
      - name: "Hacker News"
        url: "https://hnrss.org/frontpage"
      - name: "TechCrunch"
        url: "https://techcrunch.com/feed/"

# ── 사용자 관심사 (커스텀 필터) ──
interests:
  keywords:
    - "AI"
    - "요리"
    - "인테리어"
    - "숏폼"
    - "부업"
  categories:
    - "tech"
    - "food"
    - "lifestyle"
    - "finance"
  exclude_keywords:
    - "스포일러"
    - "성인"

# ── 처리 설정 ──
processing:
  transcription:
    enabled: true
    engine: "whisper"  # "whisper" (local) | "whisper.cpp" | "none"
    model: "base"      # "tiny" | "base" | "small" | "medium" | "large"
    language: "auto"   # auto-detect or force "ko", "en"
  translation:
    enabled: false
    target: "ko"
  keyword_extraction:
    enabled: true
    method: "tfidf"    # "tfidf" | "keybert" | "llm"
    max_keywords: 10
  summarization:
    enabled: false     # Requires LLM
    provider: "auto"   # "openai" | "anthropic" | "ollama"

# ── 스케줄 ──
schedule:
  mode: "daemon"       # "daemon" | "cron" | "once"
  intervals:
    tier1: "1h"        # YouTube, Reddit, RSS
    tier2: "6h"        # Naver, Google Trends
    tier3: "12h"       # TikTok, Instagram (if enabled)
  digest:
    daily: "06:00"     # Daily digest generation time
    weekly: "monday 06:00"

# ── 출력 ──
output:
  base_dir: "~/.22b/trends"   # Shared 22B Labs directory
  formats: ["md", "json"]
  digest: true
  alerts:
    enabled: true
    spike_threshold: 3.0       # 3x normal volume = alert
    keywords: ["AI", "GPT"]    # Monitor specific keywords

# ── 리소스 제한 ──
limits:
  max_storage_gb: 5
  max_videos_per_day: 100      # For transcription
  cleanup_after_days: 30
```

### 5.2 Setup Wizard

```bash
trend-radar init

# Interactive:
# 1. "어떤 분야에 관심 있으세요?" → keywords input
# 2. "어떤 플랫폼을 수집할까요?" → platform selection
# 3. "Whisper 자막 추출을 사용하시겠어요?" → Y/N
# 4. "수집 주기는?" → 1h / 6h / 24h
# 5. → config.yaml 생성
```

---

## 6. Output Format

### 6.1 Directory Structure

```
~/.22b/trends/
  ├── config.yaml                    # 사용자 설정
  │
  ├── feeds/                         # 플랫폼별 원본 데이터
  │   ├── youtube/
  │   │   ├── 2026-04-02_trending.md
  │   │   ├── 2026-04-02_shorts.md
  │   │   └── 2026-04-02.json
  │   ├── tiktok/
  │   │   ├── 2026-04-02_trending.md
  │   │   └── 2026-04-02.json
  │   ├── reddit/
  │   ├── naver/
  │   └── google_trends/
  │
  ├── keywords/                      # 키워드별 추적
  │   ├── ai.md                      # "AI" 관련 트렌드 누적
  │   ├── cooking.md
  │   └── custom-*.md
  │
  ├── digest/                        # 요약본
  │   ├── daily-2026-04-02.md
  │   ├── daily-2026-04-01.md
  │   └── weekly-2026-w14.md
  │
  ├── alerts/                        # 급상승 알림
  │   └── 2026-04-02_spike_ai.md
  │
  └── index.json                     # 메타 인덱스 (기계 소비용)
```

### 6.2 Daily Digest Example

```markdown
# 📡 Trend Radar — Daily Digest
**2026-04-02 (수요일)**

---

## 🔥 오늘의 TOP 키워드

| 순위 | 키워드 | 플랫폼 | 변동 | 점수 |
|------|--------|--------|------|------|
| 1 | AI 에이전트 | TikTok, YouTube, Naver | ↑ 340% | 97 |
| 2 | 봄 인테리어 | Instagram, Naver | ↑ 180% | 85 |
| 3 | 갤럭시 S26 | YouTube, X, Naver | NEW | 82 |
| 4 | 15분 레시피 | TikTok, YouTube | ↑ 90% | 78 |
| 5 | 부업 자동화 | Reddit, YouTube | ↑ 120% | 75 |

---

## 📺 YouTube Shorts 인기

### 1. "AI로 1분 만에 만드는 로고 디자인" (조회수 2.3M)
- 채널: @디자인공장
- 키워드: AI, 로고, 디자인, 자동화
- 자막 요약: Canva AI를 활용한 로고 제작 과정. 프롬프트 입력부터 완성까지...
- 트렌드 점수: 92/100

### 2. "이 라면 조합 진짜 미쳤다" (조회수 1.8M)
- 채널: @라면연구소
- 키워드: 라면, 레시피, 먹방
- 자막 요약: 신라면 + 까르보나라 소스 조합...
- 트렌드 점수: 87/100

---

## 🎵 TikTok 트렌딩

### 1. "POV: 퇴사 후 첫 아침" (좋아요 450K)
- @자유인김씨
- 해시태그: #퇴사 #자유 #모닝루틴 #브이로그
- 자막: "알람 없이 일어나는 첫 아침. 커피를 내리고..."
- 사용 음악: Lofi Girl - "Morning Coffee"
- 영상 스타일: 감성 브이로그, 슬로모션, 자연광

---

## 📊 Naver 실시간 검색 트렌드
1. 갤럭시 S26 출시일
2. 벚꽃 명소 2026
3. AI 자격증
4. 전세 사기 대책
5. 봄 코디 추천

---

## 🔔 Alert: "AI" 키워드 급상승 (↑ 340%)
지난 24시간 "AI" 관련 콘텐츠 생산량이 평소 대비 3.4배 증가.
주요 세부 키워드: AI 에이전트, AI 자격증, AI 로고, AI 영상 편집
→ Shorts-engine 추천: tech/tutorial 템플릿 + edgar_wright 스타일

---

*Generated by trend-radar v0.1.0 | 22B Labs*
*Next update: 2026-04-02 13:00 KST*
```

### 6.3 index.json (Machine-Readable)

```json
{
  "generated_at": "2026-04-02T06:00:00+09:00",
  "version": "0.1.0",
  "summary": {
    "total_items_collected": 312,
    "platforms_active": ["youtube", "reddit", "naver", "google_trends"],
    "top_keywords": [
      {"keyword": "AI 에이전트", "score": 97, "change_pct": 340},
      {"keyword": "봄 인테리어", "score": 85, "change_pct": 180}
    ],
    "alerts": [
      {"keyword": "AI", "type": "spike", "multiplier": 3.4}
    ]
  },
  "items": [
    {
      "platform": "youtube",
      "item_id": "abc123",
      "title": "AI로 1분 만에 만드는 로고 디자인",
      "url": "https://youtube.com/shorts/abc123",
      "metrics": {"views": 2300000, "likes": 89000},
      "keywords": ["AI", "로고", "디자인"],
      "transcript_file": "feeds/youtube/2026-04-02/abc123_transcript.md",
      "trend_score": 92,
      "collected_at": "2026-04-02T05:30:00+09:00"
    }
  ]
}
```

---

## 7. Shorts-engine Integration Interface

### 7.1 Contract

Shorts-engine reads `~/.22b/trends/index.json` when `--trend-aware` flag is used.

```bash
# Shorts-engine usage
shorts-engine run request.json --style viral_comedy --trend-aware

# What happens:
# 1. Reads ~/.22b/trends/index.json
# 2. Extracts top keywords matching user's topic/category
# 3. Injects trending keywords into scenario
# 4. Adjusts hook strategy based on current viral patterns
# 5. Adds trending hashtags to publish plan
```

### 7.2 Integration Schema

```json
{
  "$schema": "https://22blabs.dev/schemas/trend-feed-v1.json",
  "version": "1.0",
  "generated_at": "ISO timestamp",
  "summary": {
    "top_keywords": [{"keyword": "str", "score": "float", "change_pct": "float"}],
    "alerts": [{"keyword": "str", "type": "str", "multiplier": "float"}]
  },
  "items": [
    {
      "platform": "str",
      "title": "str",
      "keywords": ["str"],
      "trend_score": "float",
      "category": "str"
    }
  ]
}
```

blog-writer, MediaForge도 동일한 schema를 읽으면 됨 → **22B Labs 공용 표준**.

---

## 8. Transcription Pipeline

### 8.1 Whisper Integration

```
Video URL → yt-dlp (audio only) → Whisper → transcript.md
```

```python
# processors/transcriber.py
import whisper

class WhisperTranscriber:
    def __init__(self, model_size="base"):
        self.model = whisper.load_model(model_size)

    def transcribe(self, audio_path: str) -> dict:
        result = self.model.transcribe(audio_path, language=None)
        return {
            "text": result["text"],
            "language": result["language"],
            "segments": [
                {"start": s["start"], "end": s["end"], "text": s["text"]}
                for s in result["segments"]
            ]
        }
```

### 8.2 Model Size vs Hardware

| Model | VRAM | Speed (30s audio) | Quality | Recommended For |
|-------|------|-------------------|---------|-----------------|
| tiny | ~1GB | <1s | Basic | Raspberry Pi, low-end |
| base | ~1GB | ~2s | Good | **Default** |
| small | ~2GB | ~5s | Better | Mid-range GPU |
| medium | ~5GB | ~10s | Great | RTX 3060+ |
| large | ~10GB | ~20s | Best | RTX 4080+ (Boss's setup) |

Boss의 하드웨어(RTX 4080 Super 16GB): `medium` or `large` 권장.

---

## 9. Implementation Phases

### Phase 0: Foundation (Week 1)

```
[ ] Project scaffold (Python, Poetry)
[ ] config.yaml schema + validation
[ ] CLI: init, run, status, digest
[ ] Daemon mode skeleton (asyncio)
[ ] TrendItem dataclass + BaseCollector interface
[ ] Output: md_writer, json_writer
[ ] Tests: 15 tests
```

**Deliverable**: `trend-radar init` + `trend-radar run --once` working with empty collectors

### Phase 1: Tier 1 Collectors (Week 2-3)

```
[ ] YouTube collector (RSS + yt-dlp metadata)
[ ] Reddit collector (RSS, no auth)
[ ] Google Trends collector (pytrends)
[ ] Naver DataLab collector (Open API)
[ ] Generic RSS collector
[ ] Scheduler: interval-based collection
[ ] Tests: 20 tests
```

**Deliverable**: `trend-radar run --once` collecting real data from 4+ sources

### Phase 2: Processing Pipeline (Week 3-4)

```
[ ] Whisper transcription (local)
[ ] Keyword extraction (TF-IDF)
[ ] Category auto-classification
[ ] Trend velocity scoring
[ ] Digest builder (daily/weekly)
[ ] Alert engine (spike detection)
[ ] Tests: 15 tests
```

**Deliverable**: `trend-radar run --once` producing full daily digest MD

### Phase 3: Advanced Collectors + Daemon (Week 5-6)

```
[ ] TikTok collector (Playwright, optional)
[ ] X/Twitter collector (API v2, optional)
[ ] Instagram collector (Playwright, optional)
[ ] Daemon mode (24/7 background service)
[ ] systemd service file for Linux
[ ] Auto-cleanup (30-day retention)
[ ] Tests: 10 tests
```

**Deliverable**: `trend-radar daemon start` running 24/7 on mini PC

### Phase 4: LLM Enhancement + Polish (Week 7-8)

```
[ ] LLM summarizer (optional, same router as Shorts-engine)
[ ] KeyBERT keyword extraction (optional upgrade)
[ ] Translation processor (optional)
[ ] 22B Labs schema finalization
[ ] README (KO + EN)
[ ] Docker compose for easy deployment
[ ] Integration test with Shorts-engine --trend-aware
```

**Deliverable**: v0.1.0 release

---

## 10. Tech Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.11+ | Whisper, Playwright, NLP 생태계 |
| Package manager | Poetry | Dependency isolation |
| Async | asyncio + aiohttp | Non-blocking multi-source collection |
| Scraping | Playwright | JS rendering for TikTok/Instagram |
| Video metadata | yt-dlp | YouTube, TikTok, Instagram video info |
| Audio extraction | yt-dlp + ffmpeg | Audio-only download |
| Transcription | openai-whisper / whisper.cpp | Local, offline STT |
| Keywords | scikit-learn (TF-IDF) | Zero-dependency keyword extraction |
| Scheduling | APScheduler | In-process cron |
| Config | PyYAML + Pydantic | Schema validation |
| CLI | Click | Clean CLI interface |

---

## 11. Resource Requirements

### Minimum (Tier 1 only, no transcription)

| Resource | Requirement |
|----------|-------------|
| CPU | Any modern CPU |
| RAM | 512MB |
| Storage | 100MB/month |
| GPU | Not needed |
| Network | Periodic HTTP requests |

### Recommended (Full pipeline with Whisper)

| Resource | Requirement |
|----------|-------------|
| CPU | 4+ cores |
| RAM | 4GB+ |
| Storage | 1-2GB/month |
| GPU | CUDA GPU (for Whisper medium/large) |
| Network | Persistent (daemon mode) |

### Boss's Setup (RTX 4080 Super mini PC)

| Resource | Available |
|----------|-----------|
| CPU | Ryzen 9 7950X3D |
| RAM | 32GB DDR5 |
| GPU | RTX 4080 Super 16GB |
| Whisper model | `large` (best quality) |
| Estimated throughput | ~100 videos/hour transcription |

---

## 12. Legal & Ethical

| Platform | Method | TOS Risk | Mitigation |
|----------|--------|----------|------------|
| YouTube | RSS + public API | ✅ Safe | Official channels only |
| Reddit | RSS (no auth) | ✅ Safe | Public data, rate-limited |
| Google Trends | pytrends / API | ✅ Safe | Official API available |
| Naver | Open API | ✅ Safe | Official API with key |
| TikTok | Playwright scraping | ⚠️ Risk | Optional, user's choice, disclaimer |
| Instagram | Playwright scraping | ⚠️ Risk | Optional, user's choice, disclaimer |
| X/Twitter | API v2 free | ✅ Safe | Official API |

**Policy**: Tier 1-2 (safe) enabled by default. Tier 3 (risk) disabled by default with explicit user opt-in + disclaimer.

---

## 13. CLI Reference

```bash
# ── 초기 설정 ──
trend-radar init                      # Interactive setup wizard
trend-radar config show               # Show current config
trend-radar config edit               # Open config.yaml in editor

# ── 수집 실행 ──
trend-radar run --once                # One-shot collection
trend-radar run --once --source youtube  # Single source only
trend-radar run --once --transcribe   # Force transcription

# ── 데몬 모드 ──
trend-radar daemon start              # Start background service
trend-radar daemon stop               # Stop service
trend-radar daemon status             # Check status
trend-radar daemon logs               # Show recent logs

# ── 결과 조회 ──
trend-radar digest today              # Show today's digest
trend-radar digest yesterday          # Show yesterday's digest
trend-radar digest week               # Show weekly digest
trend-radar search "AI"               # Search collected data
trend-radar top --period 24h          # Top trending now
trend-radar top --period 7d           # Top trending this week
trend-radar alerts                    # Show active alerts

# ── 관리 ──
trend-radar stats                     # Collection statistics
trend-radar cleanup                   # Remove old data
trend-radar doctor                    # System health check
trend-radar export --format csv       # Export data
```

---

## 14. Codex Handoff Notes

### Build System
- Python 3.11+, Poetry
- `poetry install` → `poetry run trend-radar`
- Optional: `pip install trend-radar` (PyPI publish)

### Key Constraints
- Tier 1 collectors must work with zero API keys
- All processors must have offline fallback
- Output directory must be configurable (default: ~/.22b/trends)
- Never store raw video files (audio only, temporary, delete after transcription)
- Rate limiting built into every collector (respect platform limits)
- All timestamps in ISO 8601 with timezone

### Branch Strategy
```
main (stable)
└── dev/v0.1.0
    ├── feat/foundation (Phase 0)
    ├── feat/collectors-tier1 (Phase 1)
    ├── feat/processors (Phase 2)
    ├── feat/collectors-tier3 (Phase 3)
    └── feat/polish (Phase 4)
```

---

## 15. Success Criteria

| Criteria | Measurement |
|----------|-------------|
| Tier 1 collection works zero-config | `trend-radar run --once` succeeds without any API key |
| Daily digest quality | Human-readable, actionable insights |
| Whisper transcription accuracy | ≥ 85% on Korean content (base model) |
| 24/7 daemon stability | 7-day uptime without crash on mini PC |
| Shorts-engine integration | `--trend-aware` produces trend-informed scenarios |
| Collection-to-digest latency | < 5 min for full pipeline |

---

## Appendix: Quick Start

```bash
# 1. Install
git clone https://github.com/sinmb79/trend-radar.git
cd trend-radar
poetry install

# 2. Setup
poetry run trend-radar init
# → Follow wizard, set your keywords and interests

# 3. Test run
poetry run trend-radar run --once
poetry run trend-radar digest today

# 4. Start daemon (24/7)
poetry run trend-radar daemon start

# 5. Check results
cat ~/.22b/trends/digest/daily-2026-04-02.md
```

---

*22B Labs — "The 4th Path" (P4 := ⟨H⊕A⟩ ↦ Ω)*
*Your personal trend research team that never sleeps.*
