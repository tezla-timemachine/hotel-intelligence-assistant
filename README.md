# Multimodal hotel intelligence assistant

A prototype that lets a hotel manager search guest photos and reviews together in plain English. It returns the matching photos with their reviews and match scores, and, on request, a short answer written **only from that evidence**, with every point cited. **A tested prototype and a starting point, not a system for real guest data.**

**Start here:** the case study, [`docs/hotel-intelligence-09-product-case-study.md`](docs/hotel-intelligence-09-product-case-study.md). Then the annotated brief, [`docs/brief-what-we-did.docx`](docs/brief-what-we-did.docx), which says what we did under every point of the brief.

## Results in brief

| | |
|---|---|
| Search | Image search with SigLIP, filtered by the reviews' own topic and sentiment labels |
| Precision at 5, test / fresh questions | **0.81 / 0.72** (fresh questions never used before; mark: within 0.10) |
| Label accuracy | 100%: every result comes from a review with the asked-for topic and sentiment |
| Search time | 0.1–0.2 s, on this computer, free |
| Answers | Claude Sonnet 5.5 with the photos: **95.7%** of points backed by their cited evidence; about $0.013 each |
| Compared | Caption search 0.47–0.53, keyword search 0.63, image search without labels 0.54 |
| Business UAT | 12 of 12 passed |
| Known gaps | Condition questions ("dirty rooms") and two-part questions ("rooms with a city view") |
| Spend | $9.24 of a $10 budget |

## Documents

| Document | What it covers |
|---|---|
| [01 Product / business brief](docs/hotel-intelligence-01-product-business-brief.md) | Problem, product story, value in money, scope, assumptions |
| [02 Business requirements](docs/hotel-intelligence-02-business-requirements-document.md) | FR-01 to FR-18, AI quality and non-functional requirements |
| [03 Architecture and decision log](docs/hotel-intelligence-03-ai-architecture-and-decision-log.md) | Components, one database record, decisions D1–D22 |
| [04 Project plan](docs/hotel-intelligence-04-project-plan.md) and [05 schedule](docs/hotel-intelligence-05-project-schedule.csv) | Phases, milestones, Gantt chart |
| [06 Risk register](docs/hotel-intelligence-06-risk-register.md) | 14 risks with evidence |
| [07 Evaluation plan](docs/hotel-intelligence-07-evaluation-plan.md) | Questions, relevance rules, measures, pass marks, written before testing |
| [08 UAT workbook](docs/hotel-intelligence-08-user-acceptance-testing.xlsx) | Business and system tests, defects |
| [09 Case study](docs/hotel-intelligence-09-product-case-study.md) | The whole story |
| [10 Change control log](docs/hotel-intelligence-10-change-control-log.md) | Every change to models, prompts, rules and data |
| [Dataset fact sheet](docs/dataset.md) | What the source holds, the selection, and source vs generated fields |
| [Privacy](docs/privacy-and-responsible-use.md) and [limitations](docs/limitations.md) | Responsible use; what the prototype can't show |
| [Experiment log](evals/experiment-log.md) | Every model, prompt and setting tried, with cost and result |
| [Search evaluation](evals/results/20261124_search_evaluation.md), [failure analysis](evals/results/20261124_failure_analysis.md), [fresh test](evals/results/20261124_fresh_test.md) | Steps 7–9 |

Every document has a Word copy alongside it.

## Set up and run

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env    # then paste your own Anthropic API key after the = sign
```

- **The dataset** isn't in this repository: its terms are research use only. Download `ViMACSA.zip` from the link in the authors' README ([hoangquy18/Multimodal-Aspect-Category-Sentiment-Analysis](https://github.com/hoangquy18/Multimodal-Aspect-Category-Sentiment-Analysis)) into `data/raw/download/`, and check it against the SHA-256 in [`data/raw/MANIFEST.md`](data/raw/MANIFEST.md).
- **Rebuild, in order:**
  1. `scripts/select_dataset.py`: choose the 501 images, free;
  2. `scripts/translate_reviews.py` and `scripts/describe_images.py`: these send data to Claude, so check the cost first;
  3. `scripts/build_index.py`: embeddings and the database, free.
- **The image models** (CLIP and SigLIP, about 1.4 GB) go in `models/`. `scripts/embeddings.py` loads them from there with no internet access.
- **The app:**

  ```bash
  .venv/bin/streamlit run app/app.py --server.port 8507
  ```

  Then open http://localhost:8507. Search is free; each answer costs about 1 cent.
- **For a demo with no API cost,** start it in view-only mode. Search works as usual, and the answer button is hidden (D22):

  ```bash
  VIEW_ONLY=1 .venv/bin/streamlit run app/app.py --server.port 8507
  ```

## Layout

| Folder | Contents |
|---|---|
| `scripts/` | Selection, translation, descriptions, embeddings, database, search, answers, evaluation, documents |
| `prompts/` | d1 (descriptions), a1 (answers), j1 (relevance judge), g1 (answer checker) |
| `app/` | Streamlit app |
| `evals/` | Test and fresh questions, relevance guide, experiment log, results |
| `docs/` | Documents (Markdown and Word) and diagrams |

## Data and credit

Dataset: **ViMACSA**, by Nguyen, Nguyen and Van Nguyen, *New benchmark dataset and fine-grained cross-modal fusion framework for Vietnamese multimodal aspect-category sentiment analysis*, Multimedia Systems 31 (2025). Used for research only; **the photos, reviews, translations, descriptions and database are not included in this repository**. The API key lives in `.env`, which is never committed.
