"""SQLite 데이터베이스 관리 모듈."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "papers.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS papers (
    arxiv_id        TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    authors         TEXT NOT NULL,
    abstract        TEXT NOT NULL,
    categories      TEXT NOT NULL,
    pdf_url         TEXT NOT NULL,
    published       TEXT NOT NULL,
    fetched_at      TEXT NOT NULL,
    summary_ko      TEXT,
    score           INTEGER,
    favorite        INTEGER DEFAULT 0,
    matched_keyword TEXT
);

CREATE INDEX IF NOT EXISTS idx_published ON papers(published);
CREATE INDEX IF NOT EXISTS idx_favorite ON papers(favorite);
"""


def init_db() -> None:
    """DB 파일과 스키마를 생성한다."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    """row를 dict처럼 다룰 수 있는 connection을 반환한다."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def upsert_paper(paper: dict) -> bool:
    """논문을 추가한다. 이미 있으면 무시. 새로 추가됐는지 여부 반환."""
    with get_conn() as conn:
        cur = conn.execute("SELECT 1 FROM papers WHERE arxiv_id = ?", (paper["arxiv_id"],))
        if cur.fetchone():
            return False
        conn.execute(
            """
            INSERT INTO papers (arxiv_id, title, authors, abstract, categories,
                                pdf_url, published, fetched_at, matched_keyword)
            VALUES (:arxiv_id, :title, :authors, :abstract, :categories,
                    :pdf_url, :published, :fetched_at, :matched_keyword)
            """,
            paper,
        )
        return True


def get_unsummarized(limit: int = 50) -> list[sqlite3.Row]:
    """아직 요약 안 된 논문 목록."""
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT * FROM papers WHERE summary_ko IS NULL ORDER BY published DESC LIMIT ?",
            (limit,),
        )
        return cur.fetchall()


def save_summary(arxiv_id: str, summary: str) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE papers SET summary_ko = ? WHERE arxiv_id = ?", (summary, arxiv_id))


def save_score(arxiv_id: str, score: int) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE papers SET score = ? WHERE arxiv_id = ?", (score, arxiv_id))


def toggle_favorite(arxiv_id: str) -> int:
    with get_conn() as conn:
        cur = conn.execute("SELECT favorite FROM papers WHERE arxiv_id = ?", (arxiv_id,))
        row = cur.fetchone()
        if row is None:
            return 0
        new_val = 0 if row["favorite"] else 1
        conn.execute("UPDATE papers SET favorite = ? WHERE arxiv_id = ?", (new_val, arxiv_id))
        return new_val


def list_papers(
    limit: int = 50,
    offset: int = 0,
    favorite_only: bool = False,
    keyword: str | None = None,
) -> list[sqlite3.Row]:
    sql = "SELECT * FROM papers WHERE 1=1"
    params: list = []
    if favorite_only:
        sql += " AND favorite = 1"
    if keyword:
        sql += " AND (title LIKE ? OR abstract LIKE ?)"
        params += [f"%{keyword}%", f"%{keyword}%"]
    sql += " ORDER BY published DESC LIMIT ? OFFSET ?"
    params += [limit, offset]
    with get_conn() as conn:
        cur = conn.execute(sql, params)
        return cur.fetchall()


def get_paper(arxiv_id: str) -> sqlite3.Row | None:
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM papers WHERE arxiv_id = ?", (arxiv_id,))
        return cur.fetchone()


if __name__ == "__main__":
    init_db()
    print(f"DB initialized at {DB_PATH}")
