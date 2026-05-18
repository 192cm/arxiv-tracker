# CLAUDE.md

이 파일은 Claude Code가 arxiv-tracker 프로젝트에서 작업할 때 참고하는 가이드다.

## 프로젝트 목적

LLM 관련 arXiv 최신 논문을 매일 자동으로 가져와서 **Google Gemini API**로 한국어 요약하고 FastAPI 웹 UI로 보여주는 개인 논문 레이더. 부산대 생성모델 수업 과제로 시작했으며, 졸업 후에도 연구실 일상 도구로 쓸 목적.

## 아키텍처

- **수집**: `src/fetcher.py` — arxiv 패키지로 cs.CL/cs.LG/cs.AI 카테고리 + LLM 관련 키워드로 검색해 SQLite에 저장
- **요약**: `src/summarizer.py` — Google Gemini API (`google-genai` SDK)로 한국어 5섹션 요약
- **표시**: `src/app.py` — FastAPI + Jinja2 + Tailwind CDN
- **저장**: `data/papers.db` (SQLite, `db.py`가 단일 진입점)

## 컨벤션

- Python 3.11, 모든 모듈은 `src/` 패키지 안. 실행은 `python -m src.fetcher` 형태.
- 환경 변수는 `.env`. `dotenv`로 로드. `GEMINI_API_KEY`는 절대 코드/git에 들어가지 않는다.
- 새 SQL 컬럼이 필요하면 `db.py`의 `SCHEMA`만 수정하지 말고 마이그레이션 함수도 같이 작성.
- 모델 선택은 `config.yaml`의 `summary_model`에서 관리. 코드에 하드코딩하지 않는다.
- LLM provider는 Gemini로 고정. 다른 provider 추가 시 `summarizer.py`를 추상화하지 말고 별도 모듈로 분리할 것.

## 빌드/실행

```bash
conda activate arxiv
pip install -r requirements.txt
python -m src.fetcher          # 수집
python -m src.summarizer       # 요약
uvicorn src.app:app --reload   # 웹
```

## 클로드 코드 자원

- `/daily_papers` — fetch + summarize 한 번에
- `/search_topic <키워드>` — 일회성 검색
- `/my_save` — 세션 종료 전 진행상황 저장
- `paper-summary` 스킬 — 한국어 5섹션 요약 포맷 강제
- `paper-evaluator` subagent — 논문 관심도 점수

## 주의

- arXiv API는 polite하게: `client = arxiv.Client(delay_seconds=3)`. 더 짧게 줄이지 말 것.
- Gemini API는 무료 티어가 넉넉하지만 분당/일당 요청 한도가 있음. 대량 요약 시 sleep 추가 고려.
- 새 키워드 추가 시 `config.yaml`에만 추가. 코드 수정 불필요.
