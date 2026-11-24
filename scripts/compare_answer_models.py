"""Is Claude Sonnet 5.5 good enough to write the answers? A small, cheap test against Opus 5.5 (X12).

    python scripts/compare_answer_models.py

Takes 8 of the 25 test questions, reuses the exact evidence Opus was given (same 6 photos and reviews each),
asks Sonnet 5.5 to answer with the same prompt (a1), and checks Sonnet's points with the same checker (Sonnet 5.5,
prompt g1) as Opus's points were checked. Nothing already done is redone.
Writes evals/results/sonnet_sample_answers.json and evals/results/sonnet_sample_checks.csv.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import anthropic
import pandas as pd
from dotenv import load_dotenv

from answer import answer
from run_answers import LOG, LOG_FIELDS, _check

ROOT = Path(__file__).resolve().parents[1]
RESULTS, SELECTED = ROOT / "evals" / "results", ROOT / "data" / "selected"
SAMPLE = ["Q01", "Q04", "Q07", "Q09", "Q11", "Q17", "Q20", "Q24"]   # 2 visual, 3 brief, 2 detail, 1 with nothing to find


def main():
    load_dotenv(ROOT / ".env")
    client = anthropic.Anthropic()
    reviews = pd.read_csv(SELECTED / "reviews.csv").set_index("review_id")
    opus = {a["qid"]: a for a in json.loads((RESULTS / "test_answers.json").read_text())}
    prompt = (ROOT / "prompts" / "g1.txt").read_text()
    out, rows = [], []
    with LOG.open("a", newline="") as lf:
        lw = csv.DictWriter(lf, fieldnames=LOG_FIELDS)
        for qid in SAMPLE:
            o = opus[qid]
            hits = [{"image_file": it["image_file"], "review_id": it["review_id"], "labels": reviews.loc[it["review_id"], "labels"],
                     "review_en": reviews.loc[it["review_id"], "review_en"]} for it in o["items"].values()]
            r = answer(client, o["question"], hits, model="claude-sonnet-5-5")
            r.update(qid=qid, items=o["items"])
            out.append(r)
            if "credit balance" in r["status"]:
                print("!! stopped: the Anthropic account is out of credit"); break
            for n, p in enumerate((r["answer"] or {}).get("points", []), 1):
                cited = [(e, r["items"][e]) for e in p["evidence"] if e in r["items"]]
                verdict, log = (_check(client, prompt, p["point"], cited, reviews, None) if cited
                                else ({"supported": False, "reason": "no valid evidence cited"}, None))
                if log:
                    lw.writerow(log)
                rows.append({"qid": qid, "point": n, "text": p["point"], "cited": "; ".join(p["evidence"]),
                             "supported": verdict["supported"] if verdict else None,
                             "reason": verdict["reason"] if verdict else "check failed", "cost_usd": log["cost_usd"] if log else 0.0})
            print(f"{qid} {r['status']} {r['seconds']} s ${r['cost_usd']}", flush=True)
    (RESULTS / "sonnet_sample_answers.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    checks = pd.DataFrame(rows)
    checks.to_csv(RESULTS / "sonnet_sample_checks.csv", index=False)

    oc = pd.read_csv(RESULTS / "test_answer_checks.csv")
    oc = oc[oc.qid.isin(SAMPLE)]
    table = pd.DataFrame({
        "Opus 5.5": [f"{oc.supported.mean():.0%} ({int(oc.supported.sum())} of {len(oc)})",
                     sum(not opus[q]["answer"]["enough_evidence"] for q in SAMPLE),
                     f"{pd.Series([opus[q]['seconds'] for q in SAMPLE]).median():.1f} s",
                     f"${pd.Series([opus[q]['cost_usd'] for q in SAMPLE]).mean():.4f}"],
        "Sonnet 5.5": [f"{checks.supported.mean():.0%} ({int(checks.supported.sum())} of {len(checks)})",
                       sum(not a["answer"]["enough_evidence"] for a in out if a["answer"]),
                       f"{pd.Series([a['seconds'] for a in out]).median():.1f} s",
                       f"${pd.Series([a['cost_usd'] for a in out]).mean():.4f}"]},
        index=["points backed by their evidence", "answers saying 'not enough evidence'", "median time", "average cost per answer"])
    print(table.to_string())
    print(f"checking cost ${checks.cost_usd.sum():.3f}")


if __name__ == "__main__":
    main()
