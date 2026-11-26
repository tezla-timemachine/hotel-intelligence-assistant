# Dataset fact sheet (Step 1)

**What this is:** the dataset exactly as it is, checked before building anything. It records what the source gives us, what we generate or calculate ourselves, and what isn't there, as the brief asks.

**Evidence:** `data/raw/MANIFEST.md` (download record and fingerprint), `scripts/select_dataset.py` (the selection), `data/selected/` (the selected reviews and images), `data/inspection/sample_sheet.jpg` (20 sample photos, kept on this computer only).

---

## 1. Source

| | |
|---|---|
| Dataset | **ViMACSA**: Vietnamese Multimodal Aspect-Category Sentiment Analysis, hotel domain |
| Authors | Nguyen, Nguyen and Van Nguyen, *Multimedia Systems* 31 (2025); arXiv 2405.00543 |
| Where | GitHub `hoangquy18/Multimodal-Aspect-Category-Sentiment-Analysis`; the data is a Google Drive link in its README |
| File | `ViMACSA.zip`, 3.5 GB, downloaded 23 Nov 2026. SHA-256 in `data/raw/MANIFEST.md`. Deleted after selection to free disk space |
| Terms | **"Our dataset is used only for research purposes."** No open licence. So the images and reviews are **never published**: GitHub gets code, results and documents only |
| Language | **Vietnamese** reviews |

---

## 2. What's in the download

| File | What it holds |
|---|---|
| `train.json`, `dev.json`, `test.json` | **4,876 reviews** (2,876 / 1,000 / 1,000). Each has the review text, its image file names, and labels |
| `all_image_label.xlsx` | Topic labels for 14,806 images: Location, Food, Room, Facilities, Service, Public area |
| `roi_data.csv` | 14,636 boxes around objects inside images, with a topic. Not used: we don't train a model |
| `image/` | **18,311 images**. Only **9,058** belong to a review; the other 9,252 are linked to nothing, so we don't use them |

**One review** looks like this (translated):

> *"💯 the hotel has nothing to complain about 🤣"*: 2 images. Labels: Facilities **Positive**, Public area **Positive**. Each image: Facilities, Public area.

**The labels on each review** (from the source):

| Field | Meaning |
|---|---|
| `text_img_label` | The review's **topics and sentiment**, for example `Room#Negative`, from the text and images together |
| `text_label` | The same, from the text only |
| `label_each_img` | The **topics each image shows**, for example `Room`, `Food` |
| `text_one_img_label` | For each image, the review's topics and sentiments that the annotators linked to it |

**Six topics:** Location, Food, Room, Facilities, Service, Public area. **Sentiment:** Positive, Neutral, Negative.

---

## 3. The whole dataset, measured

| | |
|---|---|
| Reviews | 4,876; median **30 words** |
| Images per review | 1 (58%), 2 (21%), 3 (10%), 4–7 (11%) |
| Sentiment labels | **74% Positive**, 16% Neutral, **10% Negative** |
| Reviews with any negative point | 979 (20%) |
| Most common labels | Service Positive 2,939; Public area Positive 2,543; Room Positive 2,501 |
| Image topics | Public area 5,153; Room 3,965; Facilities 1,060; Food 520; Service 110 |

---

## 4. Our selection

**Rule** (`scripts/select_dataset.py`, seed 7): whole reviews are chosen, with all their images, so every image keeps its review. For each image topic, reviews are drawn at random until a quota of images is met, **half from reviews with a negative point and half without**. Reviews with more than 4 images are skipped, so a few don't dominate.

| | Selected |
|---|---|
| Reviews | **267** (130 with a negative point, 49%) |
| Images | **501**, all 512 × 512 pixels, colour |
| Images per review | 1 (129 reviews), 2 (65), 3 (50), 4 (23) |
| Image topics | Public area 299, Room 146, Facilities 124, Food 101, Service 36 (an image can have more than one) |
| Size on disk | 93 MB |

**Why negatives are over-sampled:** the brief's questions are mostly about complaints, and at the dataset's 20% there would be too few negative examples to test them. **This means the selection isn't representative of how guests feel overall**, and nothing here should be read as "half of guests complain".

**Sentiment by topic in the selection** (review labels):

| Topic | Positive | Neutral | Negative |
|---|---|---|---|
| Room | 103 | 26 | **57** |
| Service | 147 | 9 | 39 |
| Facilities | 62 | 32 | 39 |
| Food | 53 | 42 | 27 |
| Location | 51 | 1 | 17 |
| Public area | 132 | 56 | 12 |

---

## 5. Problems found

| Problem | Example | What it means for us |
|---|---|---|
| **The images don't always show what the review complains about** | Of 101 images from reviews negative about the **room**, only **52 show a room**. Facilities: 26 of 83 | Searching the reviews alone would return the wrong pictures. The product must check **both**: what the image shows, and what the review says. This is the brief's Step 9 failure, "the review was unrelated to the image", present in the source |
| **Reviews are in Vietnamese** | *"Phòng mùi thuốc lá nồng nặc"* (the room smells strongly of cigarettes) | Translated into English (Decision B, below) |
| **All images are resized to 512 × 512** | Every selected image | Some may look squashed. Fine for search, worth knowing |
| **Image files are JPEGs named `.png`** | All 501 selected images | Found when Claude rejected the first call. Scripts read the real format from the file |
| **Many images are unlinked** | 9,252 of 18,311 | Not used |
| **Positive reviews dominate** | 74% of labels | Over-sampled negatives in the selection (section 4) |
| **Faces may appear** | Guest photos of rooms, pools and restaurants | Privacy note in Phase 6; nothing about individuals is ever generated |

---

## 6. From the source, generated, or calculated

The brief: *"do not create fields that are not present in the source unless you clearly mark them as generated information."* Every field carries one of these tags.

| Tag | Fields |
|---|---|
| **From the source** | image file, review ID (our numbering of the source order), Vietnamese review, topic and sentiment labels, image topics, per-image labels |
| **Generated by AI** | **English translation** (`review_en`, tagged `generated: claude-opus-5-5`); image description, scene type, key objects and visible issues (tagged `generated: claude-opus-5-5, prompt d1`) |
| **Calculated by us** | embeddings (Phase 3), similarity scores, the `has_negative` flag (from the source labels) |

**Translation (Decision B, 23 Nov):** Claude Opus 5.5 translated all 267 reviews, 20 per call, for $0.75. A spot-check of 9 against the Vietnamese, 6 of them negative, kept the meaning and tone, including slang. The Vietnamese original stays beside every translation.

---

## 7. What this means for the project

1. **The labels are a gift:** "negative", "room", "food" can come from the source, not from a guess. The search can combine them with what the images show.
2. **The image–review mismatch is the central challenge.** It decides how we answer "room images with negative feedback", and it's the main thing to test.
3. **Negatives are over-sampled on purpose:** results describe search quality, not guest opinion overall.
4. **Nothing from the dataset is published,** because of its research-only terms.
