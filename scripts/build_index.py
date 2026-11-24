"""Embed every image, description and review with CLIP and SigLIP, and store them in Chroma (Steps 3-4).

    python scripts/build_index.py

Six collections in data/chroma/, one per model and kind of item:
  images_clip, images_siglip              one record per image: the picture's vector
  descriptions_clip, descriptions_siglip  one record per image: the generated description's vector
  reviews_clip, reviews_siglip            one record per review: the English review's vector

Every record carries the same metadata, so a result always leads back to its image, description and review:
image file, review ID, scene type (generated), image topics (source), the review's topic#sentiment labels
(source), and one true/false flag per label ("Room_Negative") so search can filter on them.
Rebuilding replaces the collections.
"""
from __future__ import annotations

import time
from pathlib import Path

import chromadb
import pandas as pd
from chromadb.config import Settings

from embeddings import Embedder

ROOT = Path(__file__).resolve().parents[1]
SELECTED, DB = ROOT / "data" / "selected", ROOT / "data" / "chroma"
ASPECTS = ["Location", "Food", "Room", "Facilities", "Service", "Public_area"]
POLARITY = ["Positive", "Neutral", "Negative"]


def label_flags(labels: str) -> dict:
    found = set(labels.split("; ")) if isinstance(labels, str) else set()
    flags = {f"{a}_{p}": f"{a}#{p}" in found for a in ASPECTS for p in POLARITY}
    flags["any_Negative"] = any(l.endswith("#Negative") for l in found)
    return flags


def client() -> chromadb.ClientAPI:
    return chromadb.PersistentClient(path=str(DB), settings=Settings(anonymized_telemetry=False))


def main():
    images = pd.read_csv(SELECTED / "images.csv")
    reviews = pd.read_csv(SELECTED / "reviews.csv").set_index("review_id")
    assert images.review_id.isin(reviews.index).all(), "every image must link to a selected review"
    db = client()

    def image_meta(r) -> dict:
        rev = reviews.loc[r.review_id]
        return {"image_file": r.image_file, "review_id": r.review_id, "scene_type": r.scene_type,
                "image_topics": r.image_topics, "labels": rev.labels, **label_flags(rev.labels)}

    def review_meta(rid) -> dict:
        rev = reviews.loc[rid]
        files = images[images.review_id == rid].image_file
        return {"review_id": rid, "image_files": "; ".join(files), "n_images": int(len(files)), "labels": rev.labels,
                **label_flags(rev.labels)}

    for name in ("clip", "siglip"):
        start = time.time()
        model = Embedder(name)
        vectors = {
            "images": model.images([SELECTED / "images" / f for f in images.image_file]),
            "descriptions": model.texts(list(images.description)),
            "reviews": model.texts(list(reviews.review_en)),
        }
        for kind, vec in vectors.items():
            coll_name = f"{kind}_{name}"
            if coll_name in [c.name for c in db.list_collections()]:
                db.delete_collection(coll_name)
            coll = db.create_collection(coll_name, metadata={"hnsw:space": "cosine", "model": str(name)})
            if kind == "reviews":
                ids, docs, metas = list(reviews.index), list(reviews.review_en), [review_meta(i) for i in reviews.index]
            else:
                ids = list(images.image_file)
                docs = list(images.description) if kind == "descriptions" else [f"image {f}" for f in images.image_file]
                metas = [image_meta(r) for r in images.itertuples()]
            coll.add(ids=ids, embeddings=vec.tolist(), documents=docs, metadatas=metas)
            print(f"{coll_name}: {coll.count()} records, {vec.shape[1]} numbers each")
        cut_desc = sum(model.truncated(list(images.description)))
        cut_rev = sum(model.truncated(list(reviews.review_en)))
        print(f"{name}: {time.time() - start:.0f} s; texts longer than the model reads (cut off): "
              f"descriptions {cut_desc} of {len(images)}, reviews {cut_rev} of {len(reviews)}")


if __name__ == "__main__":
    main()
