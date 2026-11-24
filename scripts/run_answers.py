"""Answer the evaluation questions with the product setting, then check the answers (Step 6-7, evaluation plan 07).

    python scripts/run_answers.py answer --questions test    # search (image, SigLIP, labels) + answer (D13) per question
    python scripts/run_answers.py check  --questions test    # Claude Sonnet checks each point against the items it cites

Answers go to evals/results/<set>_answers.json; point checks to evals/results/<set>_answer_checks.csv.
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
RESULTS, SELECTED, LOG = ROOT / "evals" / "results", ROOT / "data" / "selected", ROOT / "data" / "results" / "call_log.csv"
JUDGE, PRICE = "claude-sonnet-5-5", (2.00 / 1e6, 10.00 / 1e6)
CHECK_PROMPT = "g1"
LOG_FIELDS = ["time", "task", "model", "effort", "model_used", "status", "items", "seconds", "input_tokens",
              "output_tokens", "cost_usd", "request_id"]


def questions(which):
    return pd.read_csv(ROOT / "evals" / ("test_questions.csv" if which == "test" else "fresh_questions.csv"))


def do_answer(which: str):
    from search import Searcher
    from answer import answer
    load_dotenv(ROOT / ".env")
    client = anthropic.Anthropic()
    s = Searcher(models=("siglip",))
    out = []
    for q in questions(which).itertuples():
        hits, how = s.search(q.question, "image", "siglip")
        r = answer(client, q.question, hits)
        r.update(qid=q.qid, read_as={k: how[k] for k in ("topics", "sentiment", "look_for")},
                 items={f"E{n}": {"image_file": h["image_file"], "review_id": h["review_id"]} for n, h in enumerate(hits, 1)})
        out.append(r)
        a = r["answer"]
        print(f"{q.qid} {r['status']} {r['seconds']} s ${r['cost_usd']} enough={a['enough_evidence'] if a else None} points={len(a['points']) if a else 0}", flush=True)
        if "credit balance" in r["status"]:   # no point trying the rest: the account needs topping up (Week 5 lesson, DF-06)
            print("!! stopped: the Anthropic account is out of credit"); return
    (RESULTS / f"{which}_answers.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))


def _check(client, prompt, point, items, reviews, images) -> tuple[dict | None, dict]:
    content = [{"type": "text", "text": f"Point: {point}\n\nCited evidence:"}]
    for eid, it in items:
        rid = it["review_id"]
        content.append({"type": "text", "text": f"{eid}. Review ({rid}), labels {reviews.loc[rid, 'labels']}:\n{reviews.loc[rid, 'review_en']}\nPhoto:"})
        path = SELECTED / "images" / it["image_file"]
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/" + Image.open(path).format.lower(),
                                                    "data": base64.standard_b64encode(path.read_bytes()).decode()}})
    schema = {"type": "object", "additionalProperties": False, "required": ["supported", "reason"],
              "properties": {"supported": {"type": "boolean"}, "reason": {"type": "string"}}}
    start = time.time()
    try:
        r = client.beta.messages.create(model=JUDGE, max_tokens=500, betas=["server-side-fallback-2026-07-01"], fallbacks="default",
                                        system=prompt, output_config={"effort": "low", "format": {"type": "json_schema", "schema": schema}},
                                        messages=[{"role": "user", "content": content}])
        u, body = r.usage, next((b.text for b in r.content if b.type == "text"), "")
        verdict = json.loads(body) if body and r.stop_reason != "refusal" else None
        log = {"model_used": r.model, "status": r.stop_reason, "input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
               "cost_usd": round(u.input_tokens * PRICE[0] + u.output_tokens * PRICE[1], 5), "request_id": r._request_id}
    except anthropic.APIError as e:
        verdict, log = None, {"model_used": "", "status": f"call failed: {getattr(e, 'message', e)}"[:200], "input_tokens": 0,
                              "output_tokens": 0, "cost_usd": 0.0, "request_id": getattr(e, "request_id", "")}
    log.update(time=dt.datetime.now().isoformat(timespec="seconds"), task=f"check answer point ({CHECK_PROMPT})", model=JUDGE,
               effort="low", items=len(items), seconds=round(time.time() - start, 2))
    return verdict, log


def do_check(which: str):
    load_dotenv(ROOT / ".env")
    client = anthropic.Anthropic()
    prompt = (ROOT / "prompts" / f"{CHECK_PROMPT}.txt").read_text()
    reviews = pd.read_csv(SELECTED / "reviews.csv").set_index("review_id")
    answers = json.loads((RESULTS / f"{which}_answers.json").read_text())
    jobs = []
    for a in answers:
        for n, p in enumerate((a["answer"] or {}).get("points", []), 1):
            cited = [(e, a["items"][e]) for e in p["evidence"] if e in a["items"]]
            jobs.append((a["qid"], n, p["point"], p["evidence"], cited))
    rows = []
    with LOG.open("a", newline="") as lf, ThreadPoolExecutor(6) as pool:
        lw = csv.DictWriter(lf, fieldnames=LOG_FIELDS)
        def one(job):
            qid, n, point, cited_ids, cited = job
            if not cited:   # a point with no valid citation fails without a call
                return job, {"supported": False, "reason": "no valid evidence cited"}, None
            return job, *_check(client, prompt, point, cited, reviews, None)
        for (qid, n, point, cited_ids, cited), verdict, log in pool.map(one, jobs):
            if log:
                lw.writerow(log)
            rows.append({"qid": qid, "point": n, "text": point, "cited": "; ".join(cited_ids),
                         "supported": verdict["supported"] if verdict else None, "reason": verdict["reason"] if verdict else "check failed",
                         "cost_usd": log["cost_usd"] if log else 0.0})
    d = pd.DataFrame(rows)
    d.to_csv(RESULTS / f"{which}_answer_checks.csv", index=False)
    print(f"{len(d)} points; supported {d.supported.mean():.1%}; uncited {int((d.cited == '').sum())}; check cost ${d.cost_usd.sum():.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["answer", "check"])
    ap.add_argument("--questions", default="test", choices=["test", "fresh"])
    a = ap.parse_args()
    (do_answer if a.step == "answer" else do_check)(a.questions)
