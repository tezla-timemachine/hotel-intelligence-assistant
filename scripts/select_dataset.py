"""Select about 500 images and their reviews from ViMACSA, and extract only those images (Step 1).

    python scripts/select_dataset.py

Rule: whole reviews are selected, with every image they link to, so each image keeps its review. For each
image topic in the dataset's own labels (Room, Public_area, Facilities, Food, Service), reviews are drawn at
random (fixed seed) until the quota of images for that topic is met, half from reviews with a negative label
and half from reviews without one. Negative reviews are only 20% of the dataset, so this over-samples them on
purpose: the brief's questions are mostly about complaints. Reviews with more than 4 images are skipped, so a
few reviews don't dominate.

Reads  data/raw/labels/{train,dev,test}.json and data/raw/download/ViMACSA.zip
Writes data/selected/reviews.csv   one row per review: ID, Vietnamese text, aspect#sentiment labels (source)
       data/selected/images.csv    one row per image: file, review ID, image topics and labels (source)
       data/selected/images/       the selected images only
"""
from __future__ import annotations

import json
import random
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LABELS, ZIP, OUT = ROOT / "data" / "raw" / "labels", ROOT / "data" / "raw" / "download" / "ViMACSA.zip", ROOT / "data" / "selected"
SEED, MAX_IMAGES_PER_REVIEW = 7, 4
QUOTA = {"Room": 120, "Public_area": 50, "Facilities": 76, "Food": 70, "Service": 30}   # images per topic, half negative


def load() -> list[dict]:
    docs = []
    for split in ("train", "dev", "test"):
        for i, d in enumerate(json.load(open(LABELS / f"{split}.json", encoding="utf-8"))):
            d["review_id"], d["split"] = f"{split}-{i:04d}", split
            d["negative"] = any(l.endswith("#Negative") for l in d["text_img_label"])
            docs.append(d)
    return docs


def choose(docs: list[dict]) -> list[dict]:
    rng = random.Random(SEED)
    pool = [d for d in docs if len(d["list_img"]) <= MAX_IMAGES_PER_REVIEW]
    rng.shuffle(pool)
    chosen, ids = [], set()
    for topic, quota in QUOTA.items():
        for negative in (True, False):
            got = 0
            for d in pool:
                if got >= quota // 2:
                    break
                n = sum(topic in labels for labels in d["label_each_img"])
                if d["negative"] == negative and n and d["review_id"] not in ids:
                    chosen.append(d); ids.add(d["review_id"]); got += n
    return chosen


def main():
    docs = load()
    chosen = choose(docs)
    reviews = pd.DataFrame([{"review_id": d["review_id"], "split": d["split"], "review_vi": d["comment"],
                             "labels": "; ".join(d["text_img_label"]), "text_only_labels": "; ".join(d["text_label"]),
                             "has_negative": d["negative"], "n_images": len(d["list_img"])} for d in chosen])
    images = pd.DataFrame([{"image_file": f, "review_id": d["review_id"], "image_topics": "; ".join(d["label_each_img"][k]),
                            "image_labels": "; ".join(d["text_one_img_label"][k])}
                           for d in chosen for k, f in enumerate(d["list_img"])])
    (OUT / "images").mkdir(parents=True, exist_ok=True)
    reviews.to_csv(OUT / "reviews.csv", index=False)
    images.to_csv(OUT / "images.csv", index=False)
    # extract only the selected images, without unpacking anything else
    subprocess.run(["unzip", "-q", "-o", "-j", str(ZIP), *[f"image/{f}" for f in images.image_file], "-d", str(OUT / "images")], check=True)
    missing = [f for f in images.image_file if not (OUT / "images" / f).exists()]
    print(f"{len(reviews)} reviews, {len(images)} images; {int(reviews.has_negative.sum())} reviews with a negative label; missing files: {len(missing)}")
    topics = pd.Series([t for s in images.image_topics for t in s.split("; ")]).value_counts()
    print("image topics:", topics.to_dict())


if __name__ == "__main__":
    main()
