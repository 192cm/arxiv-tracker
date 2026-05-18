---
description: config.yaml의 키워드로 오늘치 arXiv LLM 논문을 수집하고 한국어로 요약한 뒤 상위 5개를 보여준다. 매일 아침에 호출하면 좋다.
allowed-tools: Bash, Read
---

# daily_papers

다음을 순서대로 수행하라:

1. `python -m src.fetcher` 를 실행해서 새 논문을 DB에 저장한다.
2. `python -m src.summarizer` 를 실행해서 아직 요약되지 않은 논문들을 한국어로 요약한다.
3. SQLite (`data/papers.db`)에서 가장 최근 published 기준 5개 논문의 title, arxiv_id, summary_ko를 읽어와서 보기 좋게 정리해서 사용자에게 보여준다.
4. 마지막에 "웹 UI로 더 보려면 `uvicorn src.app:app --reload` 후 http://localhost:8000 접속" 안내를 한 줄 출력한다.

오류가 나면 어디서 났는지 한국어로 짧게 알려준다. GEMINI_API_KEY가 .env에 없으면 그것부터 안내한다 (https://aistudio.google.com/apikey 에서 발급).
