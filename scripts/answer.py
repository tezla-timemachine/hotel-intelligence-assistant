"""Answer a question from the retrieved evidence only: multimodal RAG (Step 6, Decision F, D13).

    from answer import answer
    result = answer(client, question, hits)     # hits from Searcher.search()

Claude Sonnet 5.5 (CR-05; Opus 5.5 until 24 Nov) gets the question and each retrieved item as evidence E1…En: the photo itself, the English
review it came with and the review's labels. It must answer only from them, cite the items behind every point,
and say when there isn't enough evidence. Every call is logged with the model asked for and the model used (D6).
"""
from __future__ import annotations

import base64
import csv
import datetime as dt
import json
import time
from pathlib import Path

import anthropic
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMAGES, LOG = ROOT / "data" / "selected" / "images", ROOT / "data" / "results" / "call_log.csv"
MODEL, EFFORT = "claude-sonnet-5-5", "low"   # Sonnet since CR-05: better grounded than Opus on a sample, half the cost
PRICES = {"claude-opus-5-5": (4.00 / 1e6, 20.00 / 1e6), "claude-sonnet-5-5": (2.00 / 1e6, 10.00 / 1e6)}   # $ per token, in and out
PROMPT_VERSION = "a1"
SCHEMA = {"type": "object", "additionalProperties": False, "required": ["answer", "points", "enough_evidence"],
          "properties": {
              "answer": {"type": "string"},
              "points": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                                                    "required": ["point", "evidence"],
                                                    "properties": {"point": {"type": "string"},
                                                                   "evidence": {"type": "array", "items": {"type": "string"}}}}},
              "enough_evidence": {"type": "boolean"}}}
LOG_FIELDS = ["time", "task", "model", "effort", "model_used", "status", "items", "seconds", "input_tokens",
              "output_tokens", "cost_usd", "request_id"]


def _evidence(hits: list[dict]) -> list[dict]:
    content = []
    for n, h in enumerate(hits, 1):
        path = IMAGES / h["image_file"]
        media_type = "image/" + Image.open(path).format.lower()   # JPEGs named .png (fact sheet)
        content.append({"type": "text", "text": f"E{n}. Review ({h['review_id']}), labels {h['labels']}:\n{h['review_en']}\nPhoto that came with it:"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": media_type,
                                                    "data": base64.standard_b64encode(path.read_bytes()).decode()}})
    return content


def answer(client: anthropic.Anthropic, question: str, hits: list[dict], model: str = MODEL) -> dict:
    prompt = (ROOT / "prompts" / f"{PROMPT_VERSION}.txt").read_text()
    start = time.time()
    status, result, usage, model_used, request_id = "ok", None, None, "", ""
    try:
        response = client.beta.messages.create(
            model=model, max_tokens=2000, betas=["server-side-fallback-2026-07-01"], fallbacks="default",
            system=prompt, output_config={"effort": EFFORT, "format": {"type": "json_schema", "schema": SCHEMA}},
            messages=[{"role": "user", "content": [{"type": "text", "text": f"Question: {question}\n\nEvidence:"},
                                                   *_evidence(hits)]}])
        usage, model_used, request_id = response.usage, response.model, response._request_id
        text = next((b.text for b in response.content if b.type == "text"), "")
        if text and response.stop_reason != "refusal":
            result = json.loads(text)
        else:
            status = response.stop_reason
    except anthropic.APIError as e:
        status = f"call failed: {getattr(e, 'message', e)}"[:200]
    price_in, price_out = PRICES[model]
    cost = round(usage.input_tokens * price_in + usage.output_tokens * price_out, 5) if usage else 0.0
    log = {"time": dt.datetime.now().isoformat(timespec="seconds"), "task": f"answer ({PROMPT_VERSION})", "model": model,
           "effort": EFFORT, "model_used": model_used, "status": status, "items": len(hits),
           "seconds": round(time.time() - start, 2), "input_tokens": usage.input_tokens if usage else 0,
           "output_tokens": usage.output_tokens if usage else 0, "cost_usd": cost, "request_id": request_id}
    new = not LOG.exists()
    with LOG.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LOG_FIELDS)
        if new:
            w.writeheader()
        w.writerow(log)
    evidence_ids = {f"E{n}": h["image_file"] for n, h in enumerate(hits, 1)}
    return {"question": question, "status": status, "answer": result, "evidence": evidence_ids,
            "seconds": log["seconds"], "cost_usd": cost, "model_used": model_used}
