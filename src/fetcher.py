"""arXiv API로 최신 LLM 논문을 수집한다."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import arxiv
import yaml

# arXiv API 정책: 애플리케이션 식별 User-Agent 권장
arxiv._USER_AGENT = "arxiv-tracker/1.0 (kyle080405@gmail.com)"

from . import db

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_query(categories: list[str], keywords: list[str]) -> str:
    """arXiv search query 문자열을 만든다.

    카테고리 OR 조건 + 키워드 OR 조건을 AND로 묶음.
    """
    cat_q = " OR ".join(f"cat:{c}" for c in categories)
    kw_q = " OR ".join(f'abs:"{k}"' for k in keywords)
    return f"({cat_q}) AND ({kw_q})"


def match_keyword(text: str, keywords: list[str]) -> str | None:
    """어떤 키워드가 매치됐는지 첫 번째 것 반환."""
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            return kw
    return None


def fetch_recent_papers() -> list[dict]:
    """config에 정의된 키워드/카테고리로 최근 논문을 수집한다."""
    cfg = load_config()
    query = build_query(cfg["categories"], cfg["keywords"])
    cutoff = datetime.now(timezone.utc) - timedelta(days=cfg["days_back"])

    client = arxiv.Client(page_size=50, delay_seconds=3, num_retries=3)
    search = arxiv.Search(
        query=query,
        max_results=cfg["max_results"],
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    new_papers: list[dict] = []
    now_iso = datetime.now(timezone.utc).isoformat()

    for result in client.results(search):
        if result.published < cutoff:
            break  # 정렬되어 있으니 이후는 더 오래된 것

        arxiv_id = result.entry_id.rsplit("/", 1)[-1]
        haystack = f"{result.title}\n{result.summary}"
        matched = match_keyword(haystack, cfg["keywords"])
        if matched is None:
            continue  # API 매치 외에 본문 매치도 한 번 더 거름

        paper = {
            "arxiv_id": arxiv_id,
            "title": result.title.strip().replace("\n", " "),
            "authors": ", ".join(a.name for a in result.authors),
            "abstract": result.summary.strip().replace("\n", " "),
            "categories": ", ".join(result.categories),
            "pdf_url": result.pdf_url,
            "published": result.published.isoformat(),
            "fetched_at": now_iso,
            "matched_keyword": matched,
        }
        if db.upsert_paper(paper):
            new_papers.append(paper)

    return new_papers


def main() -> None:
    db.init_db()
    print("[fetcher] querying arXiv...")
    try:
        new = fetch_recent_papers()
    except Exception as e:
        print(f"[fetcher] 네트워크 오류 — arXiv에 연결할 수 없습니다: {e}")
        print("[fetcher] 기존 DB의 논문을 사용합니다.")
        return
    print(f"[fetcher] {len(new)} new papers saved")
    for p in new[:5]:
        print(f"  - {p['arxiv_id']}  {p['title'][:80]}")


if __name__ == "__main__":
    main()
