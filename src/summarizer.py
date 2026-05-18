"""미요약 논문들을 Google Gemini API로 한국어 요약한다."""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from google import genai
from google.genai import types

from . import db

load_dotenv()

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

SYSTEM_PROMPT = """당신은 LLM 분야 논문을 한국어로 요약하는 전문 도우미입니다.
주어진 영문 abstract를 읽고 정확히 아래 5개 섹션으로 정리하세요.
각 섹션은 1~3문장으로 간결하게. 모르는 내용은 추측하지 말고 "abstract만으로는 불명확"이라고 적으세요.

## 핵심 기여
이 논문이 새롭게 제안하거나 보여주는 것

## 방법론
어떤 모델/기법/접근을 사용했는지

## 결과
어떤 실험 결과를 얻었는지 (수치가 있으면 포함)

## 한계
명시되거나 추정되는 한계점

## 키워드
관련 키워드 3~5개 (쉼표로 구분)
"""


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY가 .env에 없습니다. https://aistudio.google.com/apikey 에서 발급하세요.")
    return genai.Client(api_key=api_key)


def summarize_one(
    client: genai.Client,
    model: str,
    max_tokens: int,
    title: str,
    abstract: str,
) -> str:
    user_prompt = f"# 제목\n{title}\n\n# Abstract\n{abstract}"
    response = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=max_tokens,
        ),
    )
    return (response.text or "").strip()


def main(limit: int = 20) -> None:
    cfg = load_config()
    model = cfg["summary_model"]
    max_tokens = cfg.get("max_output_tokens", 1024)

    client = build_client()
    pending = db.get_unsummarized(limit=limit)
    print(f"[summarizer] {len(pending)} papers to summarize (model={model})")

    for i, row in enumerate(pending, 1):
        try:
            summary = summarize_one(client, model, max_tokens, row["title"], row["abstract"])
            db.save_summary(row["arxiv_id"], summary)
            print(f"  [{i}/{len(pending)}] {row['arxiv_id']} done")
        except Exception as e:
            print(f"  [{i}/{len(pending)}] {row['arxiv_id']} FAILED: {e}")


if __name__ == "__main__":
    main()
