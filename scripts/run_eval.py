"""Run the search evaluation (Steps 7-8, evaluation plan 07, D14).

    python scripts/run_eval.py search  --questions test     # 6 runs x 25 questions, top 10 each; free, local
    python scripts/run_eval.py judge   --questions test     # Claude Sonnet judges each new (question, photo) pair
    python scripts/run_eval.py score   --questions test     # P@5, P@10, first-result accuracy, label accuracy, time
    python scripts/run_eval.py check                        # the judge against the dataset's own image labels

Results go to evals/results/<set>_*.csv. Judgements are kept in evals/results/judgements.csv and reused, so a
photo is judged once per question whichever run returned it.
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

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVALS, RESULTS = ROOT / "evals", ROOT / "evals" / "results"
SELECTED, LOG = ROOT / "data" / "selected", ROOT / "data" / "results" / "call_log.csv"
RUNS = [("image", "clip", True), ("image", "siglip", True), ("caption", "clip", True), ("caption", "siglip", True),
        ("keyword", "", True), ("image", "siglip", False)]
JUDGE, JUDGE_PRICE = "claude-sonnet-5-5", (2.00 / 1e6, 10.00 / 1e6)
JUDGE_PROMPT = "j1"
LOG_FIELDS = ["time", "task", "model", "effort", "model_used", "status", "items", "seconds", "input_tokens",
              "output_tokens", "cost_usd", "request_id"]
SCORED = [f"Q{i:02d}" for i in range(1, 23)]   # the edge questions Q23-Q25 are reported but not in the pass marks


def run_name(approach: str, model: str, labels: bool) -> str:
    return f"{approach}-{model}" if model else approach + ("" if labels else "")


def run_label(approach, model, labels):
    return run_name(approach, model, labels) + ("" if labels else "-nolabels")


def questions(which: str) -> pd.DataFrame:
    return pd.read_csv(EVALS / ("test_questions.csv" if which == "test" else "fresh_questions.csv"))


def do_search(which: str, only_product: bool = False):
    from search import Searcher
    s = Searcher()
    s.search("warm up", "image", "clip"); s.search("warm up", "image", "siglip")   # load each model once before timing
    rows = []
    for q in questions(which).itertuples():
        for approach, model, labels in (RUNS[1:2] if only_product else RUNS):   # RUNS[1] is the product (D17)
            hits, how = s.search(q.question, approach, model or "siglip", k=10, use_labels=labels)
            for rank, h in enumerate(hits, 1):
                rows.append({"qid": q.qid, "run": run_label(approach, model, labels), "rank": rank, "image_file": h["image_file"],
                             "score": h["score"], "seconds": how["seconds"], "labels": h["labels"],
                             "topics_read": "; ".join(how["topics"]), "sentiment_read": how["sentiment"] or ""})
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / f"{which}_retrievals.csv", index=False)
    print(f"{len(out)} results; {out[['qid', 'image_file']].drop_duplicates().shape[0]} unique question-photo pairs")


def _judge_one(client, prompt: str, rule: str, image_file: str, review: str | None) -> tuple[dict, dict]:
    from PIL import Image
    import anthropic
    path = SELECTED / "images" / image_file
    media_type = "image/" + Image.open(path).format.lower()
    schema = {"type": "object", "additionalProperties": False, "required": ["relevant", "reason"],
              "properties": {"relevant": {"type": "boolean"}, "reason": {"type": "string"}}}
    text = f"Rule: {rule}" + (f"\n\nThe review that came with the photo:\n{review}" if review else "")
    start = time.time()
    try:
        r = client.beta.messages.create(
            model=JUDGE, max_tokens=500, betas=["server-side-fallback-2026-07-01"], fallbacks="default", system=prompt,
            output_config={"effort": "low", "format": {"type": "json_schema", "schema": schema}},
            messages=[{"role": "user", "content": [{"type": "text", "text": text}, {"type": "image", "source": {
                "type": "base64", "media_type": media_type, "data": base64.standard_b64encode(path.read_bytes()).decode()}}]}])
        u = r.usage
        body = next((b.text for b in r.content if b.type == "text"), "")
        verdict = json.loads(body) if body and r.stop_reason != "refusal" else None
        log = {"model_used": r.model, "status": r.stop_reason, "input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
               "cost_usd": round(u.input_tokens * JUDGE_PRICE[0] + u.output_tokens * JUDGE_PRICE[1], 5), "request_id": r._request_id}
    except anthropic.APIError as e:
        verdict, log = None, {"model_used": "", "status": f"call failed: {getattr(e, 'message', e)}"[:200], "input_tokens": 0,
                              "output_tokens": 0, "cost_usd": 0.0, "request_id": getattr(e, "request_id", "")}
    log.update(time=dt.datetime.now().isoformat(timespec="seconds"), task=f"judge relevance ({JUDGE_PROMPT})", model=JUDGE,
               effort="low", items=1, seconds=round(time.time() - start, 2))
    return verdict, log


def do_judge(which: str, cap: float):
    import anthropic
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    client = anthropic.Anthropic()
    prompt = (ROOT / "prompts" / f"{JUDGE_PROMPT}.txt").read_text()
    qs = questions(which).set_index("qid")
    reviews = pd.read_csv(SELECTED / "reviews.csv").set_index("review_id")
    images = pd.read_csv(SELECTED / "images.csv").set_index("image_file")
    pairs = pd.read_csv(RESULTS / f"{which}_retrievals.csv")[["qid", "image_file"]].drop_duplicates()
    path = RESULTS / "judgements.csv"
    done = set()
    if path.exists():
        j = pd.read_csv(path)
        done = set(zip(j.qid, j.image_file))
    todo = [p for p in pairs.itertuples(index=False) if (p.qid, p.image_file) not in done]
    print(f"{len(todo)} pairs to judge; stop at ${cap:.2f}")
    spent, new = 0.0, not path.exists()
    with path.open("a", newline="") as jf, LOG.open("a", newline="") as lf, ThreadPoolExecutor(6) as pool:
        jw = csv.DictWriter(jf, fieldnames=["qid", "image_file", "relevant", "reason", "judge", "prompt"])
        lw = csv.DictWriter(lf, fieldnames=LOG_FIELDS)
        if new:
            jw.writeheader()
        for start in range(0, len(todo), 12):
            if spent > cap:
                print(f"!! spend ${spent:.2f} passed the cap: stopping"); break
            batch = todo[start:start + 12]
            def one(p):
                q = qs.loc[p.qid]
                review = reviews.loc[images.loc[p.image_file, "review_id"], "review_en"] if "complains about" in q.relevant_if else None
                return p, *_judge_one(client, prompt, q.relevant_if, p.image_file, review)
            out_of_credit = False
            for p, verdict, log in pool.map(one, batch):
                lw.writerow(log); spent += log["cost_usd"]
                out_of_credit |= "credit balance" in log["status"]
                if verdict is not None:
                    jw.writerow({"qid": p.qid, "image_file": p.image_file, "relevant": verdict["relevant"],
                                 "reason": verdict["reason"], "judge": JUDGE, "prompt": JUDGE_PROMPT})
            jf.flush(); lf.flush()
            if out_of_credit:
                print("!! stopped: the Anthropic account is out of credit"); break
            if (start // 12) % 10 == 0:
                print(f"{min(start + 12, len(todo))}/{len(todo)} judged, ${spent:.3f}", flush=True)
    print(f"finished: ${spent:.3f}")


def label_ok(labels: str, needed) -> bool | None:
    if not isinstance(needed, str):
        return None
    found = set(labels.split("; ")) if isinstance(labels, str) else set()
    if needed == "any_Negative":
        return any(l.endswith("#Negative") for l in found)
    if needed == "any_Positive":
        return any(l.endswith("#Positive") for l in found)
    topic, polarity = needed.rsplit("_", 1)
    if polarity == "any":
        return any(l.startswith(topic + "#") for l in found)
    return f"{topic}#{polarity}" in found


def do_score(which: str):
    qs = questions(which).set_index("qid")
    r = pd.read_csv(RESULTS / f"{which}_retrievals.csv")
    j = pd.read_csv(RESULTS / "judgements.csv")[["qid", "image_file", "relevant"]]
    r = r.merge(j, on=["qid", "image_file"], how="left")
    r["label_ok"] = [label_ok(l, qs.loc[q, "label_needed"]) for q, l in zip(r.qid, r["labels"])]
    # relevant = the photo meets the rule AND the review carries the needed label (relevance guide, section 1)
    r["hit"] = r.relevant.astype("boolean") & r.label_ok.map(lambda x: True if x is None else x).astype("boolean")
    missing = int(r.relevant.isna().sum())
    per_q = []
    for (qid, run), g in r.groupby(["qid", "run"]):
        g = g.sort_values("rank")
        top5, top10 = g[g["rank"] <= 5], g
        lab = top5.label_ok.dropna()
        per_q.append({"qid": qid, "run": run, "group": qs.loc[qid, "type"], "p_at_5": top5.hit.sum() / 5,
                      "p_at_10": top10.hit.sum() / 10, "first_ok": bool(g.iloc[0].hit), "n_returned": len(g),
                      "label_acc_5": lab.mean() if len(lab) else None, "seconds": g.seconds.iloc[0]})
    pq = pd.DataFrame(per_q)
    pq.to_csv(RESULTS / f"{which}_per_question.csv", index=False)
    scored = pq[pq.qid.isin(SCORED)] if which == "test" else pq
    summary = scored.groupby("run").agg(p_at_5=("p_at_5", "mean"), p_at_10=("p_at_10", "mean"),
                                        first_result=("first_ok", "mean"), label_accuracy=("label_acc_5", "mean"),
                                        median_seconds=("seconds", "median"), slowest_seconds=("seconds", "max")).round(3)
    summary.to_csv(RESULTS / f"{which}_summary.csv")
    wrong = r[(r["rank"] <= 5) & (r.hit == False)].merge(  # noqa: E712
        pd.read_csv(RESULTS / "judgements.csv")[["qid", "image_file", "reason"]], on=["qid", "image_file"], how="left")
    wrong.to_csv(RESULTS / f"{which}_incorrect.csv", index=False)
    print(f"unjudged results: {missing}")
    print(summary.to_string())
    print("\nby group, P@5:")
    print(pq.pivot_table(index="group", columns="run", values="p_at_5", aggfunc="mean").round(2).to_string())


# Questions whose photo rule matches one of the dataset's own image topics, so the judge can be checked against them
CHECKABLE = {"Q09": "Room", "Q12": "Room", "Q13": "Room", "Q16": "Food", "Q18": "Food",
             "Q10": "Facilities", "Q14": "Facilities", "Q11": "Public_area", "Q15": "Public_area"}


def do_check():
    """Agreement between the AI judge and the dataset's image labels (07, section 3: at least 90%)."""
    j = pd.read_csv(RESULTS / "judgements.csv")
    topics = pd.read_csv(SELECTED / "images.csv").set_index("image_file").image_topics
    j = j[j.qid.isin(CHECKABLE)].copy()
    j["label_says"] = [CHECKABLE[q] in topics[f].split("; ") for q, f in zip(j.qid, j.image_file)]
    j["agree"] = j.relevant == j.label_says
    print(f"{len(j)} judgements checkable against the image labels; agreement {j.agree.mean():.1%}")
    print(j.groupby("qid").agree.agg(["mean", "size"]).round(2).to_string())
    print(pd.crosstab(j.relevant, j.label_says, rownames=["judge"], colnames=["image label"]))
    j[~j.agree].to_csv(RESULTS / "judge_disagreements.csv", index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["search", "judge", "score", "check"])
    ap.add_argument("--questions", default="test", choices=["test", "fresh"])
    ap.add_argument("--cap", type=float, default=2.5)
    ap.add_argument("--only-product", action="store_true", help="search with the chosen approach only (image, SigLIP, labels)")
    a = ap.parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    {"search": lambda: do_search(a.questions, a.only_product), "judge": lambda: do_judge(a.questions, a.cap),
     "score": lambda: do_score(a.questions), "check": do_check}[a.step]()
