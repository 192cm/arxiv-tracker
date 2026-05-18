# arxiv-tracker

LLM 관련 arXiv 최신 논문을 매일 자동으로 가져와서 **Google Gemini API**로 한국어 요약하고, 웹페이지로 보여주는 개인 논문 레이더.

## 설치

```bash
conda create -n arxiv python=3.11 -y
conda activate arxiv
pip install -r requirements.txt
```

Gemini API 키 발급 (1분 소요, 무료 티어 넉넉함): https://aistudio.google.com/apikey

`.env` 파일 만들기:

```bash
cp .env.example .env
# .env 열어서 GEMINI_API_KEY 채우기
```

## 사용법

### 1. CLI

```bash
python -m src.fetcher          # 최근 논문 수집 (평일: days_back=1, 월요일: days_back=3 권장)
python -m src.summarizer       # 수집된 논문 중 미요약본 요약
```

### 2. 웹 UI

```bash
uvicorn src.app:app --reload --port 8000
```

브라우저에서 `http://localhost:8000` 접속.

### 3. Claude Code에서 자연어로

프로젝트 폴더에서 `claude` 실행 후:

```
/daily_papers       # 오늘치 논문 자동 수집 + 요약 + 결과 보기
/search_topic RAG   # 특정 주제 검색
/my_save            # 세션 종료 전 진행상황 저장
```

## 설정

`config.yaml`에서 키워드, 카테고리, 모델명, `days_back` 등 수정 가능.

## 클로드 코드 기법 사용 내역

본 프로젝트는 코드 작성/관리 과정에서 다음 Claude Code 기능을 활용했다 (요약 LLM은 Gemini를 쓰되, 개발 도구로는 Claude Code 사용).

- **Custom Slash Commands**: `/daily_papers`, `/search_topic`, `/my_save`
- **Skills**: `paper-summary` — 논문 요약 포맷 자동 적용
- **Subagent**: `paper-evaluator` — 논문 품질 점수
- **Hook**: PreCompact — 진행상황 자동 백업
