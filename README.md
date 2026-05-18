<div align="center">

# 📡 arxiv-tracker

**Personal LLM Paper Radar** — Automatically fetches the latest arXiv papers daily, summarizes them in Korean via Gemini, and serves them through a clean web UI

<br>

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Gemini-flash--lite-4285F4?style=flat-square&logo=google&logoColor=white)](https://aistudio.google.com/)
[![Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-D97706?style=flat-square&logo=anthropic&logoColor=white)](https://claude.ai/code)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

<br>

[Features](#-features) · [Quick Start](#-quick-start) · [Usage](#-usage) · [Configuration](#️-configuration) · [Architecture](#️-architecture) · [Claude Code](#-claude-code-integration)

</div>

---

## ✨ Features

- **Auto Fetch** — Pulls LLM-related papers from cs.CL / cs.LG / cs.AI categories with keyword filtering
- **Korean Summaries** — Gemini API summarizes each abstract into 5 structured sections (contribution / method / results / limitations / keywords)
- **Web UI** — Tailwind-styled page with search, favorites, and paper detail view
- **SQLite Storage** — Deduplicates papers and tracks summarization status persistently
- **Claude Code Integration** — One command `/daily_papers` runs the full fetch → summarize → display pipeline

---

## 🚀 Quick Start

### 1. Set up the environment

```bash
conda create -n arxiv python=3.11 -y
conda activate arxiv
pip install -r requirements.txt
```

### 2. Get a Gemini API key

[Google AI Studio](https://aistudio.google.com/apikey) — takes 1 minute, free tier is more than enough

```bash
cp .env.example .env
# Open .env and fill in GEMINI_API_KEY=
```

### 3. Run

```bash
python -m src.fetcher      # fetch papers
python -m src.summarizer   # summarize unsummarized papers
uvicorn src.app:app --reload --port 8000
```

Open `http://localhost:8000` in your browser.

---

## 📖 Usage

### CLI

```bash
# Fetch papers based on keywords/categories in config.yaml
python -m src.fetcher

# Summarize all pending papers
python -m src.summarizer
```

> On Mondays, set `days_back: 3` in `config.yaml` to include weekend papers.

### Web UI

```bash
uvicorn src.app:app --reload --port 8000
```

| Route | Description |
|-------|-------------|
| `/` | Paper list with search and favorites filter |
| `/paper/{arxiv_id}` | Paper detail with Korean summary |

### Claude Code

Run `claude` inside the project folder:

```
/daily_papers          # fetch + summarize + display top 5 papers in one shot
/search_topic RAG      # one-off topic search (not saved to DB)
/my_save               # persist session decisions to CLAUDE.md
```

---

## ⚙️ Configuration

Everything is controlled through `config.yaml` — no code changes needed to add keywords or swap models.

| Key | Default | Description |
|-----|---------|-------------|
| `summary_model` | `gemini-3.1-flash-lite` | Gemini model for summarization |
| `max_output_tokens` | `1024` | Max tokens per summary |
| `categories` | `cs.CL, cs.LG, cs.AI` | arXiv categories to search |
| `keywords` | LLM, RAG, RLHF … | Title/abstract filter keywords |
| `max_results` | `50` | Max papers fetched per run |
| `days_back` | `3` | How many days back to look |

<details>
<summary>Full keyword list</summary>

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

## 🏗️ Architecture

```
arxiv-tracker/
├── src/
│   ├── fetcher.py      # arXiv API → SQLite
│   ├── summarizer.py   # SQLite → Gemini API → Korean summary
│   ├── app.py          # FastAPI web server
│   ├── db.py           # Single SQLite entry point
│   └── templates/      # Jinja2 + Tailwind HTML
├── config.yaml         # Model, keywords, categories
├── .env                # API keys (git-ignored)
└── data/papers.db      # SQLite DB (git-ignored)
```

**Data flow**

```
arXiv API
   │  arxiv client (delay_seconds=3)
   ▼
fetcher.py ──▶ data/papers.db
                    │  unsummarized rows
                    ▼
             summarizer.py ──▶ Gemini API
                    │  Korean summary
                    ▼
             data/papers.db (summary_ko column)
                    │
                    ▼
              app.py (FastAPI)
                    │
                    ▼
             http://localhost:8000
```

> The runtime LLM (Gemini) and the development tool (Claude Code) are intentionally separate — Gemini summarizes papers, Claude Code writes and debugs the code.

---

## 🤖 Claude Code Integration

This project uses [Claude Code](https://claude.ai/code) as the development tool throughout.

| Feature | Location | Role |
|---------|----------|------|
| **CLAUDE.md** | `CLAUDE.md` | Injects project rules and conventions into every Claude session |
| **Slash Commands** | `.claude/commands/` | Automates `/daily_papers`, `/search_topic`, `/my_save` |
| **Skills** | `.claude/skills/paper-summary/` | Enforces the 5-section summary format consistently |
| **Subagent** | `.claude/agents/paper-evaluator.md` | Scores each paper 1–10 by relevance to user interests |
| **Hooks** | `.claude/settings.json` | PreCompact auto-backup · Stop completion beep |
| **Auto Memory** | `~/.claude/projects/…/memory/` | Persists user context across sessions |

For a detailed walkthrough of each technique, open [`claude_tech_overview.html`](claude_tech_overview.html) in a browser.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `arxiv` | arXiv API client |
| `google-genai` | Gemini API SDK |
| `fastapi` + `uvicorn` | Web server |
| `jinja2` | HTML templating |
| `python-dotenv` | `.env` loading |
| `pyyaml` | `config.yaml` parsing |

---

## 📄 License

MIT © 2025 [192cm](https://github.com/192cm)
