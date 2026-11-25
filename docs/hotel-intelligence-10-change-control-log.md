# Change Control Log: Multimodal Hotel Intelligence Assistant

> **Status:** started 23 Nov 2026. Every change to something that affects the AI's results, or what's been agreed, is recorded here, with its evidence and who approved it. Then the affected evaluation is re-run.

---

## 1. What needs change control

| Item | Why it matters | Current version |
|---|---|---|
| **Dataset selection** | Changes what can be found | 501 images, 267 reviews, seed 7 (D3) |
| **Translation** (model, prompt) | Changes the English text that's searched and shown | Claude Opus 5.5, effort low, prompt in `scripts/translate_reviews.py` (D4) |
| **Description model and prompt** | Changes caption search and scene types | Claude Opus 5.5, effort low, prompt `prompts/d1.txt` (D8) |
| **Embedding models** | Change every similarity score | CLIP ViT-B/32 and SigLIP base-patch16-224, saved in `models/` (D10) |
| **Search rules** (labels, K, thresholds) | Change what's returned | Rules on topic and sentiment words; review-label filter; K = 6 (`scripts/search.py`, D12) |
| **Answer model and prompt** | Change what the manager reads | Claude **Sonnet** 5.5, effort low, prompt `prompts/a1.txt`, with the photos (CR-05, D16) |
| **Test questions and relevance rules** | Change what "correct" means | 25 test and 10 fresh questions; `evals/relevance-guide.md`; Claude Sonnet 5.5 as judge (D14) |
| **Requirements** (02) and pass marks (07) | Change what's agreed | BRD v1.0; evaluation plan v1.0 with pass marks (D14) |

Routine edits that don't change results (typos, layout, refactoring without changing output) don't need a change request.

## 2. How a change is made

1. Describe the change and why.
2. Show the evidence: a test, a result, a cost.
3. The Product Owner approves or rejects.
4. Make the change, record the new version above, and re-run the affected evaluation.

## 3. Change register

| ID | Date | Change | Affects | Evidence | Approved by |
|---|---|---|---|---|---|
| CR-01 | 23 Nov 2026 | Reviews translated into English, with the Vietnamese original kept (Decision B) | Data, search text | Managers read English; spot-check of 9 kept the meaning; $0.75 | Product Owner (D4) |
| CR-02 | 23 Nov 2026 | Selection quotas trimmed (Public area 120 → 50, Room 120, Facilities 80 → 76): 585 images became 501 | Dataset selection | The first run gave 585 images; the brief asks for about 500 | Product Owner (D3, D7) |
| CR-03 | 23 Nov 2026 | Image descriptions added with prompt d1 (Decision C) | Data, caption search | Trial of 10 checked side by side; all 501 done, $4.10 | Product Owner (D8) |
| CR-04 | 23 Nov 2026 | Question rules fixed: plurals match ("bathrooms"); more negative words (dislike, hate, awful, rude, noisy, broken, worn…); "room" with a facility word ("spa treatment rooms") isn't a guest room; visible words (dirty, worn, broken) stay in the search text; leftover small words dropped | Search rules | First run misread 3 of 25 questions. After: all 25 read correctly; label accuracy 96% → 100%; SigLIP image search P@5 0.81 → 0.81, P@10 0.81 → 0.82, first result 77% → 77%. Tuned on the test questions, so the fresh questions decide whether it holds | Product Owner (D15) |
| CR-05 | 24 Nov 2026 | Answer model: Claude Opus 5.5 → **Claude Sonnet 5.5** | Answer model | 8-question sample on identical evidence: points backed 78% → 100%; $0.025 → $0.013 per answer; 8.0 s → 5.9 s (X12) | Product Owner (D16) |
| CR-06 | 25 Nov 2026 | **View-only mode** added to the app (`VIEW_ONLY=1`): the answer button is hidden, so no API calls | App | Tested in the browser: an example search returned 6 photos in 0.07 s; no answer button; a view-only note in the sidebar | Product Owner (D22) |
