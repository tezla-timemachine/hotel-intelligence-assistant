"""Natural-language search over the hotel images and reviews (Step 5, Decision I, D12).

    from search import Searcher
    s = Searcher()
    hits, how = s.search("Show room images associated with negative feedback")
    hits, how = s.similar("image_18846_0.png")            # search by image (image to text)

A question is read by rules: topic words ("room", "breakfast", "pool") pick the review topics, sentiment words
("negative", "complaints", "good") pick the review sentiment. Only images whose review carries those labels are
searched, and they're ranked by how well they match what's left of the question ("room images"). Images can't
show how a guest felt, so sentiment always comes from the review's own label.

Approaches, for the comparison in Step 8:
  image    the question's words against the photo itself (CLIP or SigLIP)
  caption  the question's words against Claude's description of the photo (CLIP or SigLIP text encoder)
  keyword  the question's words against the description and key objects, by word overlap (BM25), no embeddings
Every search is logged in data/results/search_log.csv.
"""
from __future__ import annotations

import csv
import datetime as dt
import math
import re
import time
from collections import Counter
from pathlib import Path

import pandas as pd

from build_index import client
from embeddings import Embedder

ROOT = Path(__file__).resolve().parents[1]
SELECTED, LOG = ROOT / "data" / "selected", ROOT / "data" / "results" / "search_log.csv"
K = 6

# Words that point to the dataset's six review topics. Phrases are matched before single words.
TOPIC_WORDS = {
    "Room": ["guest room", "bedroom", "bathroom", "toilet", "shower", "bedding", "sheets", "room", "rooms", "bed", "beds", "suite"],
    "Food": ["breakfast", "buffet", "food", "meal", "meals", "dinner", "lunch", "restaurant", "dish", "dishes", "drinks", "menu"],
    "Facilities": ["swimming pool", "facilities", "facility", "pool", "pools", "gym", "spa", "sauna", "massage", "amenities", "equipment", "wifi", "lift", "elevator"],
    "Public_area": ["public areas", "public area", "common areas", "lobby", "reception area", "hallway", "corridor", "garden", "entrance", "building", "exterior"],
    "Service": ["service", "staff", "check-in", "housekeeping", "employees"],
    "Location": ["location", "beach", "neighbourhood", "neighborhood", "nearby", "surroundings"],
}
SENTIMENT_WORDS = {
    "Negative": ["negative", "complaints", "complaint", "complain", "complained", "bad", "poor", "dirty", "unhappy",
                 "disappointed", "disappointing", "worst", "problems", "problem", "issues", "unpleasant", "criticism",
                 "dislike", "disliked", "hate", "hated", "awful", "terrible", "horrible", "rude", "noisy", "smelly",
                 "broken", "unclean", "worn"],
    "Positive": ["positive", "praise", "praised", "good", "great", "excellent", "best", "happy", "liked", "loved",
                 "love", "nice", "beautiful", "favourite", "favorite", "enjoyed"],
}
# Words that only frame the request; dropped before matching against the images
FILLER = ["show me", "show", "find", "images", "image", "photos", "photo", "pictures", "related to", "associated with",
          "connected with", "mentioned in", "about", "reviews", "review", "feedback", "comments", "comment", "customers",
          "guests", "what are", "saying", "the main", "main", "in these", "shown", "these", "the", "of", "with", "in",
          "and", "a", "an", "for", "to", "are", "is", "or", "from", "that", "what", "do", "does", "most", "them",
          "on", "at", "me", "my", "any"]
# Sentiment words that also describe something a photo can show: they set the sentiment AND stay in the search text (CR-04)
VISIBLE = ["dirty", "worn", "broken", "unclean", "stained", "beautiful"]
DEFAULT_VIEW = {"Room": "hotel room", "Food": "food", "Facilities": "hotel facilities", "Public_area": "hotel lobby",
                "Service": "hotel reception", "Location": "hotel view"}


def _find(text: str, words: list[str]) -> bool:
    # "bathrooms" matches "bathroom": an optional plural ending on every word (CR-04)
    return any(re.search(rf"\b{re.escape(w)}(s|es)?\b", text) for w in words)


# "room" alone doesn't mean a guest room when a facility is named with it ("spa treatment rooms", "gym room") (CR-04)
FACILITY_ROOMS = ["spa", "gym", "sauna", "massage", "treatment", "meeting", "function", "game", "games", "dining", "breakfast"]


def read_question(question: str) -> dict:
    """Split a question into topics, sentiment and what to look for in the images (D12)."""
    q = question.lower().strip()
    topics = [t for t, words in TOPIC_WORDS.items() if _find(q, words)]
    room_words = [w for w in TOPIC_WORDS["Room"] if w not in ("room", "rooms")]
    if "Room" in topics and not _find(q, room_words) and _find(q, FACILITY_ROOMS):
        topics.remove("Room")
    sentiment = next((s for s, words in SENTIMENT_WORDS.items() if _find(q, words)), None)
    look_for = q
    dropped = [w for w in SENTIMENT_WORDS["Negative"] + SENTIMENT_WORDS["Positive"] if w not in VISIBLE] + FILLER
    for w in sorted(dropped, key=len, reverse=True):
        look_for = re.sub(rf"\b{re.escape(w)}(s|es)?\b", " ", look_for)
    look_for = re.sub(r"[^\w\s-]", " ", look_for)
    look_for = " ".join(look_for.split())
    if not look_for:
        look_for = " ".join(DEFAULT_VIEW[t] for t in topics) or "hotel"
    return {"topics": topics, "sentiment": sentiment, "look_for": f"a photo of {look_for}"}


def label_filter(topics: list[str], sentiment: str | None) -> dict | None:
    """The Chroma filter on the review labels: any of the topics, with the sentiment if one was asked for."""
    polarities = [sentiment] if sentiment else ["Positive", "Neutral", "Negative"]
    if not topics:
        return {"any_Negative": True} if sentiment == "Negative" else (
            {"$or": [{f"{a}_Positive": True} for a in TOPIC_WORDS]} if sentiment == "Positive" else None)
    flags = [{f"{t}_{p}": True} for t in topics for p in polarities]
    return flags[0] if len(flags) == 1 else {"$or": flags}


class Searcher:
    def __init__(self, models: tuple[str, ...] = ("clip", "siglip")):
        self.db = client()
        self.models = {m: Embedder(m) for m in models}
        self.images = pd.read_csv(SELECTED / "images.csv").set_index("image_file")
        self.reviews = pd.read_csv(SELECTED / "reviews.csv").set_index("review_id")
        # keyword search: one bag of words per image, from the generated description, objects and scene type
        docs = (self.images.description + " " + self.images.key_objects.fillna("") + " " + self.images.scene_type)
        self._bags = {f: Counter(re.findall(r"\w+", d.lower())) for f, d in docs.items()}
        self._avg_len = sum(sum(b.values()) for b in self._bags.values()) / len(self._bags)
        self._df = Counter(w for b in self._bags.values() for w in b)

    def _bm25(self, query: str, files: list[str]) -> list[tuple[str, float]]:
        words = re.findall(r"\w+", query.lower().replace("a photo of", ""))
        n = len(self._bags)
        scores = []
        for f in files:
            bag, length = self._bags[f], sum(self._bags[f].values())
            s = sum(math.log(1 + (n - self._df[w] + 0.5) / (self._df[w] + 0.5)) * bag[w] * 2.2 /
                    (bag[w] + 1.2 * (0.25 + 0.75 * length / self._avg_len)) for w in words if w in bag)
            scores.append((f, round(s, 4)))
        return sorted(scores, key=lambda x: -x[1])

    def _hit(self, f: str, score: float) -> dict:
        img = self.images.loc[f]
        rev = self.reviews.loc[img.review_id]
        return {"image_file": f, "score": score, "review_id": img.review_id, "scene_type": img.scene_type,
                "description": img.description, "visible_issues": img.visible_issues if isinstance(img.visible_issues, str) else "",
                "image_topics": img.image_topics, "labels": rev.labels, "review_en": rev.review_en, "review_vi": rev.review_vi}

    def search(self, question: str, approach: str = "image", model: str = "siglip", k: int = K,
               use_labels: bool = True) -> tuple[list[dict], dict]:
        start = time.time()
        how = read_question(question)
        where = label_filter(how["topics"], how["sentiment"]) if use_labels else None
        how.update(approach=approach, model=model if approach != "keyword" else "", filter=where)
        if approach == "keyword":
            allowed = list(self.images.index) if where is None else self.db.get_collection("images_clip").get(where=where)["ids"]
            ranked = self._bm25(how["look_for"], allowed)[:k]
        else:
            coll = self.db.get_collection(f"{'images' if approach == 'image' else 'descriptions'}_{model}")
            t0 = time.time()
            vec = self.models[model].texts([how["look_for"]]).tolist()
            how["embed_seconds"] = round(time.time() - t0, 3)
            r = coll.query(query_embeddings=vec, n_results=k, where=where, include=["distances"])
            ranked = [(i, round(1 - d, 4)) for i, d in zip(r["ids"][0], r["distances"][0])]
        hits = [self._hit(f, s) for f, s in ranked]
        how["seconds"] = round(time.time() - start, 3)
        self._log(question, how, hits)
        return hits, how

    def similar(self, image_file: str, model: str = "siglip", k: int = K) -> tuple[list[dict], dict]:
        """Search by image: the photos that look most like this one, with their reviews (image to text)."""
        start = time.time()
        coll = self.db.get_collection(f"images_{model}")
        vec = coll.get(ids=[image_file], include=["embeddings"])["embeddings"]
        r = coll.query(query_embeddings=[list(vec[0])], n_results=k + 1, include=["distances"])
        ranked = [(i, round(1 - d, 4)) for i, d in zip(r["ids"][0], r["distances"][0]) if i != image_file][:k]
        hits = [self._hit(f, s) for f, s in ranked]
        how = {"topics": [], "sentiment": None, "look_for": f"images like {image_file}", "approach": "similar image",
               "model": model, "filter": None, "seconds": round(time.time() - start, 3)}
        self._log(f"[similar to {image_file}]", how, hits)
        return hits, how

    def _log(self, question: str, how: dict, hits: list[dict]):
        LOG.parent.mkdir(parents=True, exist_ok=True)
        new = not LOG.exists()
        with LOG.open("a", newline="") as fh:
            w = csv.writer(fh)
            if new:
                w.writerow(["time", "question", "approach", "model", "topics", "sentiment", "look_for", "results", "scores", "seconds"])
            w.writerow([dt.datetime.now().isoformat(timespec="seconds"), question, how["approach"], how["model"],
                        "; ".join(how["topics"]), how["sentiment"] or "", how["look_for"],
                        "; ".join(h["image_file"] for h in hits), "; ".join(str(h["score"]) for h in hits), how["seconds"]])
