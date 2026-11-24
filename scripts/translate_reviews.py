"""Translate the selected Vietnamese reviews into English with Claude (Decision B, Step 1).

    python scripts/translate_reviews.py

The Vietnamese original stays in `review_vi`; the translation goes in `review_en` and is tagged as generated
(source = "generated: claude-opus-5-5"), as the brief requires. Reviews go 20 to a call, and every call is
logged with its model, tokens, time and cost in data/results/call_log.csv.

Reads  data/selected/reviews.csv
Writes data/selected/reviews.csv (adds review_en, review_en_source)
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import time
from pathlib import Path

import anthropic
import pandas as pd
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
REVIEWS, LOG = ROOT / "data" / "selected" / "reviews.csv", ROOT / "data" / "results" / "call_log.csv"
MODEL, EFFORT, PRICE_IN, PRICE_OUT = "claude-opus-5-5", "low", 4.00 / 1e6, 20.00 / 1e6
BATCH = 20
LOG_FIELDS = ["time", "task", "model", "effort", "model_used", "status", "items", "seconds", "input_tokens",
              "output_tokens", "cost_usd", "request_id"]

PROMPT = """You translate Vietnamese hotel guest reviews into natural English.
Rules:
- Translate the meaning faithfully. Keep the guest's tone: praise, complaints, sarcasm and emphasis.
- Don't add, remove, soften or summarise anything. Keep names of places and hotels as written.
- Keep emoji as they are. Write slang and abbreviations ("kh" = "không") as their plain English meaning.
- Return one translation per review, with its review_id unchanged."""

SCHEMA = {"type": "object", "additionalProperties": False, "required": ["translations"],
          "properties": {"translations": {"type": "array", "items": {
              "type": "object", "additionalProperties": False, "required": ["review_id", "english"],
              "properties": {"review_id": {"type": "string"}, "english": {"type": "string"}}}}}}


def translate(client: anthropic.Anthropic, batch: pd.DataFrame) -> tuple[dict, dict]:
    reviews = [{"review_id": r.review_id, "vietnamese": r.review_vi} for r in batch.itertuples()]
    start = time.time()
    response = client.beta.messages.create(
        model=MODEL, max_tokens=8000, betas=["server-side-fallback-2026-07-01"], fallbacks="default",
        system=PROMPT, output_config={"effort": EFFORT, "format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": json.dumps(reviews, ensure_ascii=False)}])
    u = response.usage
    log = {"time": dt.datetime.now().isoformat(timespec="seconds"), "task": "translate reviews", "model": MODEL,
           "effort": EFFORT, "model_used": response.model, "status": response.stop_reason, "items": len(batch),
           "seconds": round(time.time() - start, 2), "input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
           "cost_usd": round(u.input_tokens * PRICE_IN + u.output_tokens * PRICE_OUT, 5), "request_id": response._request_id}
    text = next((b.text for b in response.content if b.type == "text"), "")
    found = {t["review_id"]: t["english"] for t in json.loads(text)["translations"]} if text else {}
    return found, log


def main():
    load_dotenv(ROOT / ".env")
    client = anthropic.Anthropic()
    reviews = pd.read_csv(REVIEWS)
    english = dict(zip(reviews.review_id, reviews.get("review_en", pd.Series([None] * len(reviews)))))
    todo = reviews[[not isinstance(english.get(i), str) for i in reviews.review_id]]
    LOG.parent.mkdir(parents=True, exist_ok=True)
    new_log = not LOG.exists()
    spent = 0.0
    with LOG.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LOG_FIELDS)
        if new_log:
            w.writeheader()
        for start in range(0, len(todo), BATCH):
            batch = todo.iloc[start:start + BATCH]
            found, log = translate(client, batch)
            w.writerow(log); fh.flush()
            spent += log["cost_usd"]
            missing = [i for i in batch.review_id if i not in found]
            english.update(found)
            print(f"{start + len(batch)}/{len(todo)} translated, ${spent:.3f} so far{'; missing: ' + ', '.join(missing) if missing else ''}", flush=True)
    reviews["review_en"] = reviews.review_id.map(english)
    reviews["review_en_source"] = f"generated: {MODEL}"
    reviews.to_csv(REVIEWS, index=False)
    print(f"done: {reviews.review_en.notna().sum()} of {len(reviews)} reviews in English, ${spent:.3f}")


if __name__ == "__main__":
    main()
