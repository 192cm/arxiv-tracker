# arxiv-tracker: LLM 논문 자동 요약 레이더

**과제 제출자**: (이름) / (학번)
**수업**: 생성모델 — Claude Code 실습
**제출일**: 2026-05-20

---

## 1. 프로젝트 소개

매일 arXiv에 올라오는 LLM 관련 논문을 일일이 확인하기는 부담스럽다. 이 프로젝트는 관심 키워드(LLM, RAG, agent, alignment 등)로 arXiv 최신 논문을 자동 수집하고, **Google Gemini API**로 한국어 5섹션 요약을 생성한 뒤, FastAPI 기반 웹 UI로 보여주는 개인 논문 레이더다.

**주요 기능**
- arXiv 카테고리(cs.CL, cs.LG, cs.AI)와 키워드 기반 자동 수집
- Gemini(`gemini-3.1-flash-lite`)로 한국어 요약 (핵심 기여 / 방법론 / 결과 / 한계 / 키워드)
- SQLite로 영구 저장, 즐겨찾기 및 검색 지원
- Tailwind 스타일의 깔끔한 웹 인터페이스

**LLM 선택 근거**

요약 백엔드로 `gemini-3.1-flash-lite`를 선택한 이유는 다음과 같다.

1. **무료 티어**: Google AI Studio의 무료 할당량(분당 RPM, 일당 RPD)이 개인용 데일리 트래킹에 충분
2. **속도**: Flash-Lite 모델은 abstract 수준의 짧은 입력에 대해 응답이 빠름
3. **한국어 품질**: 최신 Gemini는 한국어 자연스러움이 양호
4. **설정 분리**: `config.yaml`의 `summary_model`만 바꾸면 Pro 등 다른 모델로 전환 가능

개발 과정에서는 별도로 **Claude Code**(Anthropic의 터미널 기반 코딩 에이전트)를 활용해 코드 작성/리팩토링/디버깅을 수행했다. 즉, **런타임 LLM(Gemini)**과 **개발 도구(Claude Code)**가 분리된 구조다.

**스크린샷**
(여기에 웹 UI 메인 화면 캡처)
(여기에 논문 상세 페이지 캡처)

---

## 2. 사용한 Claude Code 기법

본 프로젝트는 과제 요구사항의 5가지 기법 중 **4가지**(custom slash command, skills, subagent, hook)를 사용했다.

### 2.1 Custom Slash Commands (`.claude/commands/`)

세 가지 자주 쓰는 작업을 슬래시 명령으로 만들었다.

| 명령 | 역할 |
|------|------|
| `/daily_papers` | fetcher + summarizer를 순차 실행하고 결과 5개 출력 |
| `/search_topic <키워드>` | 일회성 주제 검색 (DB 저장 없음) |
| `/my_save` | 세션 종료 전 진행상황을 CLAUDE.md에 저장 |

매번 `python -m src.fetcher && python -m src.summarizer`를 치는 대신 `/daily_papers` 한 번으로 끝난다.

(여기에 `/daily_papers` 실행 결과 캡처)

### 2.2 Skills (`paper-summary`)

`.claude/skills/paper-summary/SKILL.md`에 한국어 요약 포맷(핵심 기여/방법론/결과/한계/키워드)을 정의했다. description에 "논문 abstract를 요약할 때 자동 호출"이라고 명시해, Claude Code가 논문 관련 작업을 인식하면 자동으로 이 형식을 따른다. 덕분에 `summarizer.py`의 SYSTEM_PROMPT(Gemini에게 전달)와 Claude Code 안에서의 요약이 일관된 포맷을 갖는다.

### 2.3 Subagent (`paper-evaluator`)

`.claude/agents/paper-evaluator.md`에 정의된 subagent는 논문의 관심 적합도, 신규성, 실용성, 임팩트 가능성을 가중 평균해 1~10점을 매긴다. 메인 세션의 context를 아끼면서 평가 작업만 분리할 수 있다는 점이 핵심 장점이다.

### 2.4 Hook (PreCompact)

`/update-config` 자연어 명령으로 PreCompact 훅을 설정했다. 컨텍스트가 자동 압축되기 전에 진행상황을 CLAUDE.md에 자동 백업해서, 긴 세션에서도 맥락이 유실되지 않는다.

(여기에 `.claude/settings.json` 일부 캡처)

---

## 3. 사용법

### 설치

```bash
conda create -n arxiv python=3.11 -y
conda activate arxiv
pip install -r requirements.txt
echo "GEMINI_API_KEY=AIza..." > .env
```

Gemini API 키는 https://aistudio.google.com/apikey 에서 발급.

### 실행

```bash
# CLI 방식
python -m src.fetcher       # 새 논문 수집
python -m src.summarizer    # 한국어 요약
uvicorn src.app:app --reload --port 8000

# Claude Code 방식 (더 간단)
claude
> /daily_papers
```

브라우저에서 `http://localhost:8000` 접속.

> **참고**: 월요일에는 주말치 논문까지 포함하려면 `config.yaml`의 `days_back`를 `3`으로 설정한다.

---

## 4. 배운 점과 한계

- 슬래시 명령과 스킬을 같이 쓰면 "명시적 호출(명령)"과 "암묵적 호출(스킬)"이 자연스럽게 결합된다. 예를 들어 `/daily_papers`를 호출하면 그 안에서 자동으로 paper-summary 스킬의 포맷 규칙이 참조된다.
- Hook은 자연어로 설정 가능해서 진입장벽이 낮았다. 다만 `.claude/settings.json` 직접 수정도 익혀두면 디버깅이 쉬워진다.
- **런타임 LLM(Gemini)과 개발 도구(Claude Code)를 분리**한 설계가 의외로 자연스러웠다. Claude Code가 Gemini SDK 호출 코드를 작성하고 디버깅해주는 구조.
- 개발 중 발견한 이슈: `arxiv` v4.0.0은 내부적으로 `requests`를 쓰므로 User-Agent를 `arxiv._USER_AGENT`로 오버라이드해야 arXiv의 429 차단을 피할 수 있었다. 신버전 Starlette에서는 `TemplateResponse` 호출 방식도 변경됐다(`request=` 키워드 인자로 분리). 라이브러리 버전 변화에 대한 주의가 필요하다.
- **한계**: 현재는 abstract만 요약하므로 깊은 분석은 제한적. 향후 PDF 다운로드 후 본문까지 요약하는 기능을 추가할 예정.
