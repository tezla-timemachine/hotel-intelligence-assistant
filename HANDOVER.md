# Project Handover: Multimodal Hotel Intelligence Assistant

## 1. What this is
A Week 7 prototype. Guest photos and reviews from ViMACSA are embedded with SigLIP and CLIP into a Chroma database on this computer. A question is read by rules into a topic, a sentiment and what to look for; photos are filtered by the review labels and ranked by similarity; Claude Sonnet 5.5 answers from the shown evidence on request. Story: case study (09). Every brief point: `docs/week7-plan.md`.

## 2. Data
- ViMACSA (research use only): 501 photos and 267 reviews in `data/selected/` (not in Git). Download record and SHA-256: `data/raw/MANIFEST.md`. The zip itself was deleted to save disk space.
- Generated fields are tagged in the files: `review_en` (Claude Opus 5.5), `description`, `scene_type`, `key_objects`, `visible_issues` (Claude Opus 5.5, prompt d1).

## 3. Status
- All 7 phases done; business UAT 12 of 12 (D18); fresh test passed (D20).
- Product setting: image search, SigLIP, review-label filter, top 6; answers Claude Sonnet 5.5, effort low, prompt a1.
- API spend: $9.24 of $10.

## 4. How it works (short)
`scripts/search.py` (read the question → label filter → Chroma similarity → log) → `scripts/answer.py` (evidence E1–E6 → cited answer → log) → `app/app.py`. Embeddings: `scripts/embeddings.py`; database build: `scripts/build_index.py`. Every model call: `data/results/call_log.csv` (model asked for and used, D6). Every search: `data/results/search_log.csv`.

## 5. Running it
See README. App: `.venv/bin/streamlit run app/app.py --server.port 8507`. Search is free and local; an answer sends the 6 shown photos and reviews to Anthropic (about 1 cent). For demos: `VIEW_ONLY=1` in front of the same command hides the answer button, so there's no API cost (D22).

## 6. Conventions
- **Cheapest suitable model first** (D16): Haiku for simple high-volume text, Sonnet for descriptions, answers and judging; a dearer model only after a small test shows it's needed, and with the Product Owner's yes.
- Every decision in the decision log (03); every change to models, prompts, rules or data in the change log (10), then re-run the affected evaluation.
- Data sent to Claude only with the Product Owner's approval; the key stays in `.env`.
- Documents: Markdown is the master; Word copies via `scripts/build_word.py`.

## 7. Open issues and to-dos
| Item | Where |
|---|---|
| Hybrid search (image + keyword on visible issues) for condition questions | DF-07, failure analysis |
| Two-part questions ("rooms with a city view") | DF-08, fresh test |
| Broad questions: count complaints from the labels first | Failure analysis |
| Agree with users whether a sitting area counts as "a room" | DF-02 |
| Re-run translation with Haiku and descriptions with Sonnet if the data is rebuilt | D16 |
| Remove Moondream and Ollama from Week 5 (about 1.6 GB) if disk space is needed | Week 5 handover |
