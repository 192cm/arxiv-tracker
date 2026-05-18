"""FastAPI 기반 논문 조회 웹 UI."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from . import db

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="arxiv-tracker")


@app.on_event("startup")
def _startup() -> None:
    db.init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request, q: str | None = None, fav: int = 0):
    papers = db.list_papers(limit=100, favorite_only=bool(fav), keyword=q)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"papers": papers, "q": q or "", "fav": fav},
    )


@app.get("/paper/{arxiv_id}", response_class=HTMLResponse)
def paper_detail(request: Request, arxiv_id: str):
    paper = db.get_paper(arxiv_id)
    if paper is None:
        return HTMLResponse("Not found", status_code=404)
    return templates.TemplateResponse(
        request=request,
        name="paper.html",
        context={"paper": paper},
    )


@app.post("/paper/{arxiv_id}/favorite")
def fav_toggle(arxiv_id: str):
    db.toggle_favorite(arxiv_id)
    return RedirectResponse(url=f"/paper/{arxiv_id}", status_code=303)
