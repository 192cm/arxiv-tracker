---
description: 특정 주제 키워드로 arXiv를 즉석에서 검색하고 상위 결과를 한국어 요약과 함께 보여준다. config.yaml과 별개로 일회성 검색이 필요할 때 사용.
allowed-tools: Bash, Read, Write
argument-hint: <검색할 주제 키워드>
---

# search_topic

사용자가 인자로 넣은 주제 `$ARGUMENTS` 에 대해 다음을 수행하라:

1. `arxiv` 파이썬 패키지로 해당 주제 관련 최신 논문 5편을 가져온다. 카테고리는 cs.CL, cs.LG, cs.AI로 제한.
2. 각 논문의 abstract를 paper-summary 스킬 형식에 맞춰 한국어로 요약한다.
3. 결과를 다음 형식으로 출력한다:

```
## [N] 제목
- arxiv_id: ...
- 저자: ...
- published: YYYY-MM-DD
- 링크: https://arxiv.org/abs/...

(여기에 paper-summary 형식 요약)
```

검색 인자가 없으면 사용자에게 어떤 주제를 검색할지 물어본다.
이 명령은 DB에 저장하지 않는다 (일회성 탐색용).
