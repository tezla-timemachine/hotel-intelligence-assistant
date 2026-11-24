"""The two multimodal embedding models, loaded from models/ with no network (D10).

Both put images and text into one shared space, so a text question can be compared directly with a picture.
Every vector is normalised to length 1, so the similarity of two vectors is their dot product (cosine).

    from embeddings import Embedder
    clip = Embedder("clip")
    clip.images(["data/selected/images/image_1_0.png"])   # -> array (1, 512)
    clip.texts(["a hotel swimming pool"])                 # -> array (1, 512)
"""
from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")          # models are on disk; never call the internet
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

import numpy as np
import torch
from PIL import Image
from transformers import AutoModel, AutoProcessor

ROOT = Path(__file__).resolve().parents[1]
MODELS = {"clip": ROOT / "models" / "clip-vit-base-patch32", "siglip": ROOT / "models" / "siglip-base-patch16-224"}
# The longest text each model reads, in tokens; longer text is cut off at this point
MAX_TOKENS = {"clip": 77, "siglip": 64}


class Embedder:
    def __init__(self, name: str):
        self.name = name
        self.model = AutoModel.from_pretrained(MODELS[name]).eval()
        self.processor = AutoProcessor.from_pretrained(MODELS[name])

    def _normalise(self, x: torch.Tensor) -> np.ndarray:
        return torch.nn.functional.normalize(x, dim=-1).cpu().numpy().astype("float32")

    @torch.no_grad()
    def images(self, paths: list[str | Path], batch: int = 16) -> np.ndarray:
        out = []
        for i in range(0, len(paths), batch):
            pics = [Image.open(p).convert("RGB") for p in paths[i:i + batch]]
            inputs = self.processor(images=pics, return_tensors="pt")
            out.append(self._normalise(self._vector(self.model.get_image_features(**inputs))))
        return np.concatenate(out)

    @torch.no_grad()
    def texts(self, texts: list[str], batch: int = 32) -> np.ndarray:
        out = []
        for i in range(0, len(texts), batch):
            inputs = self.processor(text=texts[i:i + batch], return_tensors="pt", truncation=True,
                                    max_length=MAX_TOKENS[self.name],
                                    padding="max_length" if self.name == "siglip" else True)   # SigLIP was trained on padded text
            out.append(self._normalise(self._vector(self.model.get_text_features(**inputs))))
        return np.concatenate(out)

    @staticmethod
    def _vector(features) -> torch.Tensor:
        # Transformers 5 can return a model output instead of a bare tensor
        return features if isinstance(features, torch.Tensor) else features.pooler_output

    def truncated(self, texts: list[str]) -> list[bool]:
        """Which texts are longer than the model can read (they get cut off)."""
        lengths = [len(ids) for ids in self.processor.tokenizer(texts, truncation=False)["input_ids"]]
        return [n > MAX_TOKENS[self.name] for n in lengths]
