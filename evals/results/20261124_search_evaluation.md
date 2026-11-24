# Search evaluation and comparison (Steps 7–8)

**Run:** 23–24 Nov 2026, as set in the evaluation plan (07, D14). 25 test questions (`evals/test_questions.csv`), 6 search runs, top 10 results each: 1,500 results. Every photo judged by Claude Sonnet 5.5 against the written rule (`evals/relevance-guide.md`), seeing only the photo and the rule; review labels checked automatically. The question rules were fixed once after the first run (CR-04); these are the results after the fix. The 10 fresh questions are still unseen (Phase 7).

**Scored on Q01–Q22.** The three edge questions (Q23–Q25) are reported separately: two of them have nothing to find.

Files: `test_retrievals.csv` (every result), `judgements.csv` (every verdict and reason), `test_per_question.csv`, `test_summary.csv`, `test_incorrect.csv`, `test_answers.json`, `test_answer_checks.csv`. First run before the fix: `test_summary_run1.csv`.

---

## 1. The comparison (the brief's Step 8 table)

| Approach | Retrieval quality: P@5 | P@10 | First result right | Response time (median) | Notes |
|---|---|---|---|---|---|
| **Multimodal search: image, SigLIP** | **0.81** | **0.82** | **77%** | 0.06 s | **Best overall.** Strongest on facilities, public areas and bathrooms |
| Multimodal search: image, CLIP | 0.80 | 0.73 | 77% | 0.03 s | Close behind; better on rooms and "dirty or worn" |
| Caption search: keyword (BM25) | 0.63 | 0.61 | 68% | 0.02 s | Finds details the descriptions name ("balcony", "stains"); fails when words differ ("bathrooms" P@5 0) |
| Caption search: SigLIP text | 0.53 | 0.48 | 45% | 0.06 s | Cuts off a third of the descriptions at 64 tokens (R-13) |
| Caption search: CLIP text | 0.47 | 0.47 | 59% | 0.03 s | Built to match text with images, weak at text with text |
| Multimodal search: image, SigLIP, **no labels** | 0.54 | 0.53 | 50% | 0.05 s | Only **47%** of results come from reviews with the asked-for sentiment |

All runs with labels: **100% label accuracy** (every result's review carries the topic and sentiment asked for).

**Which works better, and why:** **multimodal search on the image itself, with SigLIP**, using the reviews' own labels for topic and sentiment.
- The photo is the evidence a manager wants to see, so matching the question **directly to the photo** beats matching it to a written description of the photo. Descriptions add a second, lossy step: the description may not mention what's asked, and CLIP and SigLIP's text encoders aren't built to compare two texts.
- **SigLIP edges CLIP** on P@10 (0.82 against 0.73): it stays relevant further down the list.
- **The labels are essential:** without them, half the results show rooms guests loved when asked for complaints. Images can't show sentiment; reviews can.

## 2. By kind of question (P@5)

| Group | Caption CLIP | Caption SigLIP | Image CLIP | **Image SigLIP** | No labels | Keyword |
|---|---|---|---|---|---|---|
| Visual (Q01–Q08) | 0.45 | 0.48 | 0.78 | **0.82** | 0.82 | 0.68 |
| The brief's examples (Q09–Q16) | 0.57 | 0.50 | 0.80 | **0.82** | 0.32 | 0.65 |
| Detail (Q17–Q22) | 0.37 | 0.63 | **0.83** | 0.77 | 0.43 | 0.53 |
| Edge (Q23–Q25) | 0.07 | 0.07 | 0.07 | 0.00 | 0.00 | 0.00 |

- **Visual questions don't need the labels** (0.82 with or without): there's no sentiment to filter on.
- **The brief's examples depend on them:** 0.82 with, 0.32 without.

## 3. Where image search fails (input to the failure analysis, Step 9)

| Question | SigLIP image P@5 | What happened |
|---|---|---|
| Q06 Bedrooms with a balcony | 0.0 | Balconies found, but not **with** the bedroom: two things in one photo |
| Q17 Dirty or worn rooms | 0.0 | Ordinary rooms returned: **dirt isn't something embeddings see**. CLIP and keyword search did better (0.6), helped by descriptions that name stains |
| Q05 Sea views | 0.6 | Views of cities and rooftops mixed in |
| Q09, Q12, Q13 Room questions | 0.8 | The first result is a room's sitting area (TV, sofa, no bed), ruled "not a bedroom" under our wording (D15) |
| Q23 What do guests dislike most? | 0.0 | Too broad: no topic to look for |
| Q24, Q25 Gym, spa | 0.0 | Nothing to find, as expected |

**Incorrect retrievals** in the top 5, all 25 questions (125 results per run): image-SigLIP 36, image-CLIP 36, keyword 56, caption-SigLIP 66, caption-CLIP 72, no labels 66. Listed with the judge's reasons in `test_incorrect.csv`.

## 4. Answers (Step 6, product setting)

Image search with SigLIP, top 6, answered by Claude Opus 5.5 (prompt a1) with the photos.

| Measure | Result | Pass mark | |
|---|---|---|---|
| Answers returned | 25 of 25 | | ✓ |
| Answer time | median **7.4 s**, slowest 12.4 s | under 15 s | ✓ |
| Answer cost | average **$0.026**, highest $0.029 | under $0.05 | ✓ |
| Points citing evidence | 115 of 115 | every point | ✓ |
| Points backed by what they cite | **87.8%** (101 of 115) | at least 95% | **✗ missed** |
| Honest gaps: gym (Q24), spa (Q25) | **2 of 2** said "not enough evidence" | 2 of 2 | ✓ |

**The 14 unsupported points** (`test_answer_checks.csv`) are mostly **over-description of photos**: details applied to both photos when only one shows them ("umbrellas", "patterned chairs"), or positions wrong ("showerhead beneath the window"). Two **generalise too far** ("room problems are the most repeated complaint" from two reviews). **None invents a complaint** a guest didn't make. Answers also flagged weak evidence themselves on 4 more questions (Q11, Q15, Q17, Q23), saying the photos don't show what the reviews complain about.

## 5. Pass marks: summary

| Measure | Result | Mark | |
|---|---|---|---|
| P@5 (Q01–Q22) | 0.81 | ≥ 0.80 | ✓ |
| First result right | 77% | ≥ 85% | ✗ accepted (D15) |
| Label accuracy with the filter | 100% | 100% | ✓ |
| Search time | 0.06 s | < 2 s | ✓ |
| Answer time | 7.4 s | < 15 s | ✓ |
| Answer cost | $0.029 at most | < $0.05 | ✓ |
| Grounded points | 87.8% | ≥ 95% | ✗ |
| Honest gaps | 2 of 2 | 2 of 2 | ✓ |
| Judge against image labels | 87.7% | ≥ 90% | ✗ accepted (D15): definitions, not errors |
| Fresh questions | Phase 7 | within 0.10 of P@5 | — |

**Cost of this evaluation:** judging $2.54, answers $0.64, answer checks $0.37. Project spend: **$8.50 of $10**.
