<div align="center">

# 📡 arxiv-tracker

**LLM 논문 레이더** — arXiv 최신 논문을 매일 자동 수집하고 Gemini로 한국어 요약해서 웹으로 보여준다

<br>

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Gemini-flash--lite-4285F4?style=flat-square&logo=google&logoColor=white)](https://aistudio.google.com/)
[![Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-D97706?style=flat-square&logo=anthropic&logoColor=white)](https://claude.ai/code)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

<br>

[기능](#-기능) · [빠른 시작](#-빠른-시작) · [사용법](#-사용법) · [설정](#️-설정) · [아키텍처](#️-아키텍처) · [Claude Code](#-claude-code-활용)

</div>

---

## ✨ 기능

- **자동 수집** — cs.CL / cs.LG / cs.AI 카테고리에서 LLM 관련 논문을 키워드 필터링해 가져온다
- **한국어 요약** — Gemini API로 핵심 기여 / 방법론 / 결과 / 한계 / 키워드 5섹션 요약
- **웹 UI** — 검색, 즐겨찾기, 논문 상세 보기를 갖춘 Tailwind 기반 페이지
- **SQLite 저장** — 중복 없이 논문을 영구 보관, 요약 여부 상태 관리
- **Claude Code 통합** — `/daily_papers` 한 줄로 수집→요약→출력까지 자동화

---

## 🚀 빠른 시작

### 1. 환경 세팅

```bash
conda create -n arxiv python=3.11 -y
conda activate arxiv
pip install -r requirements.txt
```

### 2. API 키 발급

[Google AI Studio](https://aistudio.google.com/apikey) → 1분, 무료 티어로도 충분

```bash
cp .env.example .env
# .env 열어서 GEMINI_API_KEY= 채우기
```

### 3. 실행

```bash
python -m src.fetcher      # 논문 수집
python -m src.summarizer   # 한국어 요약
uvicorn src.app:app --reload --port 8000
```

브라우저에서 `http://localhost:8000` 접속

---

## 📖 사용법

### CLI

```bash
# 논문 수집 (config.yaml의 keywords/categories 기준)
python -m src.fetcher

# 미요약 논문 일괄 요약
python -m src.summarizer
```

> 월요일에는 주말치까지 포함하려면 `config.yaml`의 `days_back`을 `3`으로 설정

### 웹 UI

```bash
uvicorn src.app:app --reload --port 8000
```

| 경로 | 설명 |
|------|------|
| `/` | 논문 목록 (검색, 즐겨찾기 필터) |
| `/paper/{arxiv_id}` | 논문 상세 + 한국어 요약 |

### Claude Code에서

프로젝트 폴더에서 `claude` 실행 후:

```
/daily_papers          # 수집 + 요약 + 상위 5편 출력 (원스톱)
/search_topic RAG      # 특정 주제 일회성 검색 (DB 저장 안 함)
/my_save               # 세션 결정사항을 CLAUDE.md에 반영
```

---

## ⚙️ 설정

모든 동작은 `config.yaml` 하나로 제어한다. 코드 수정 없이 키워드·모델을 바꿀 수 있다.

| 항목 | 기본값 | 설명 |
|------|--------|------|
| `summary_model` | `gemini-3.1-flash-lite` | 요약에 사용할 Gemini 모델 |
| `max_output_tokens` | `1024` | 요약 최대 토큰 수 |
| `categories` | `cs.CL, cs.LG, cs.AI` | arXiv 카테고리 |
| `keywords` | LLM, RAG, RLHF … | 제목/abstract 필터 키워드 |
| `max_results` | `50` | 1회 수집 최대 논문 수 |
| `days_back` | `3` | 최근 며칠치 가져올지 |

<details>
<summary>키워드 목록 보기</summary>

```yaml
keywords:
  - "large language model"
  - "LLM"
  - "language model"
  - "in-context learning"
  - "chain-of-thought"
  - "RAG"
  - "retrieval-augmented"
  - "LLM agent"
  - "tool use"
  - "fine-tuning"
  - "instruction tuning"
  - "RLHF"
  - "alignment"
  - "prompt"
```

</details>

---

## 🏗️ 아키텍처

```
arxiv-tracker/
├── src/
│   ├── fetcher.py      # arXiv API → SQLite 수집
│   ├── summarizer.py   # SQLite → Gemini API → 한국어 요약 저장
│   ├── app.py          # FastAPI 웹 서버
│   ├── db.py           # SQLite 단일 진입점
│   └── templates/      # Jinja2 + Tailwind HTML
├── config.yaml         # 모델·키워드·카테고리 설정
├── .env                # API 키 (git 제외)
└── data/papers.db      # SQLite DB (git 제외)
```

**데이터 흐름**

```
arXiv API
   │  arxiv 패키지 (delay_seconds=3)
   ▼
fetcher.py ──▶ data/papers.db
                    │  미요약 논문
                    ▼
             summarizer.py ──▶ Gemini API
                    │  한국어 요약
                    ▼
             data/papers.db (summary_ko 컬럼)
                    │
                    ▼
              app.py (FastAPI)
                    │
                    ▼
             브라우저 http://localhost:8000
```

> 런타임 LLM(Gemini)과 개발 도구(Claude Code)를 분리한 구조 — Gemini가 논문을 요약하고, Claude Code가 코드를 작성·디버깅한다

---

## 🤖 Claude Code 활용

이 프로젝트는 개발 도구로 [Claude Code](https://claude.ai/code)를 적극 활용했다.

| 기술 | 파일 | 역할 |
|------|------|------|
| **CLAUDE.md** | `CLAUDE.md` | 프로젝트 규칙·컨벤션을 Claude에 자동 주입 |
| **Slash Commands** | `.claude/commands/` | `/daily_papers`, `/search_topic`, `/my_save` 자동화 |
| **Skills** | `.claude/skills/paper-summary/` | 5섹션 요약 형식 표준화 |
| **Subagent** | `.claude/agents/paper-evaluator.md` | 논문 관심도 1~10점 자동 채점 |
| **Hooks** | `.claude/settings.json` | PreCompact 자동 백업 · Stop 완료 알림 |
| **Auto Memory** | `~/.claude/projects/…/memory/` | 세션 간 사용자 컨텍스트 유지 |

기술별 상세 설명은 [`claude_tech_overview.html`](claude_tech_overview.html)을 브라우저로 열어서 확인.

---

## 📦 의존성

| 패키지 | 용도 |
|--------|------|
| `arxiv` | arXiv API 클라이언트 |
| `google-genai` | Gemini API SDK |
| `fastapi` + `uvicorn` | 웹 서버 |
| `jinja2` | HTML 템플릿 |
| `python-dotenv` | `.env` 로드 |
| `pyyaml` | `config.yaml` 파싱 |

---

## 📄 라이선스

MIT © 2025 [192cm](https://github.com/192cm)
