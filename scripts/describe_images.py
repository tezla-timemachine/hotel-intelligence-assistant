"""Describe each selected image with a vision language model (Step 2, Decision C).

    python scripts/describe_images.py --sample 10     # 2 images per topic, to judge quality and cost first
    python scripts/describe_images.py --all           # every image not yet described

Each answer fills a fixed form: scene type, a one-or-two-sentence description, key objects and visible issues.
All four are generated and tagged with the model and prompt version. Answers are appended to
data/selected/descriptions.jsonl as they arrive; every call goes to data/results/call_log.csv, with the model
asked for and the model used (D6).
"""
from __future__ import annotations

import argparse
import base64
import csv
import datetime as dt
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import anthropic
import pandas as pd
from dotenv import load_dotenv
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SELECTED, LOG = ROOT / "data" / "selected", ROOT / "data" / "results" / "call_log.csv"
OUT = SELECTED / "descriptions.jsonl"
MODEL, EFFORT, PRICE_IN, PRICE_OUT = "claude-opus-5-5", "low", 4.00 / 1e6, 20.00 / 1e6
PROMPT_VERSION = "d1"
SCENES = ["room", "bathroom", "pool", "restaurant", "food", "lobby", "exterior", "view", "facility", "public area", "other"]
SCHEMA = {"type": "object", "additionalProperties": False,
          "required": ["scene_type", "description", "key_objects", "visible_issues"],
          "properties": {"scene_type": {"type": "string", "enum": SCENES},
                         "description": {"type": "string"},
                         "key_objects": {"type": "array", "items": {"type": "string"}},
                         "visible_issues": {"type": "array", "items": {"type": "string"}}}}
LOG_FIELDS = ["time", "task", "model", "effort", "model_used", "status", "items", "seconds", "input_tokens",
              "output_tokens", "cost_usd", "request_id"]


def describe(client: anthropic.Anthropic, image_file: str, prompt: str) -> tuple[dict, dict]:
    path = SELECTED / "images" / image_file
    media_type = "image/" + Image.open(path).format.lower()   # the files are named .png but stored as JPEG
    data = base64.standard_b64encode(path.read_bytes()).decode()
    start = time.time()
    try:
        response = client.beta.messages.create(
            model=MODEL, max_tokens=2000, betas=["server-side-fallback-2026-07-01"], fallbacks="default",
            system=prompt, output_config={"effort": EFFORT, "format": {"type": "json_schema", "schema": SCHEMA}},
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}},
                {"type": "text", "text": "Describe this hotel photo."}]}])
    except anthropic.APIError as e:   # logged with the API's message, never guessed
        log = {"time": dt.datetime.now().isoformat(timespec="seconds"), "task": f"describe image ({PROMPT_VERSION})",
               "model": MODEL, "effort": EFFORT, "model_used": "", "status": f"call failed: {getattr(e, 'message', e)}"[:200],
               "items": 1, "seconds": round(time.time() - start, 2), "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0,
               "request_id": getattr(e, "request_id", "")}
        return {"image_file": image_file, "source": "", "answer": None, "status": "call failed"}, log
    u = response.usage
    log = {"time": dt.datetime.now().isoformat(timespec="seconds"), "task": f"describe image ({PROMPT_VERSION})",
           "model": MODEL, "effort": EFFORT, "model_used": response.model, "status": response.stop_reason, "items": 1,
           "seconds": round(time.time() - start, 2), "input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
           "cost_usd": round(u.input_tokens * PRICE_IN + u.output_tokens * PRICE_OUT, 5), "request_id": response._request_id}
    assert log["model"] and log["model_used"], "D6: every call must record the model asked for and the model used"
    text = next((b.text for b in response.content if b.type == "text"), "")
    answer = json.loads(text) if text and response.stop_reason != "refusal" else None
    return {"image_file": image_file, "source": f"generated: {MODEL}, prompt {PROMPT_VERSION}", "answer": answer,
            "status": "ok" if answer else response.stop_reason}, log


def main():
    ap = argparse.ArgumentParser()
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--sample", type=int, help="describe this many images, spread across the topics")
    group.add_argument("--all", action="store_true", help="describe every image not yet described")
    ap.add_argument("--cap", type=float, default=4.0, help="stop starting new calls once this run's spend passes this many dollars")
    args = ap.parse_args()
    load_dotenv(ROOT / ".env")
    client = anthropic.Anthropic()
    prompt = (ROOT / "prompts" / f"{PROMPT_VERSION}.txt").read_text()
    images = pd.read_csv(SELECTED / "images.csv")
    done = {r["image_file"] for r in map(json.loads, OUT.open()) if r["status"] == "ok"} if OUT.exists() else set()
    todo = images[~images.image_file.isin(done)]
    if args.sample:
        per = max(1, args.sample // 5)
        picks = [todo[todo.image_topics.str.contains(t)].sample(per, random_state=11) for t in ("Room", "Public_area", "Facilities", "Food", "Service")]
        todo = pd.concat(picks).drop_duplicates("image_file").head(args.sample)
    files = list(todo.image_file)
    print(f"{len(files)} images to describe; stop at ${args.cap:.2f}")
    new_log = not LOG.exists()
    spent = 0.0
    with LOG.open("a", newline="") as lf, OUT.open("a") as out, ThreadPoolExecutor(4) as pool:
        w = csv.DictWriter(lf, fieldnames=LOG_FIELDS)
        if new_log:
            w.writeheader()
        for start in range(0, len(files), 4):
            if spent > args.cap:
                print(f"!! spend ${spent:.2f} passed the ${args.cap:.2f} cap: stopping"); break
            for rec, log in pool.map(lambda f: describe(client, f, prompt), files[start:start + 4]):
                out.write(json.dumps(rec, ensure_ascii=False) + "\n"); w.writerow(log); spent += log["cost_usd"]
            out.flush(); lf.flush()
            if (start + 4) % 40 == 0:
                print(f"{min(start + 4, len(files))}/{len(files)} described, ${spent:.3f}", flush=True)
    print(f"finished: ${spent:.4f} for this run")


if __name__ == "__main__":
    main()
