# Evaluation Plan: Multimodal Hotel Intelligence Assistant

> **Status:** v1.0, approved 23 Nov 2026 with Decision G option B (D14). **Written before any test was run**, so the pass marks aren't fitted to the results (D5). Changes after approval go through the change control log (10).

---

## 1. What we want to know

| Question | Measure | Brief step |
|---|---|---|
| Does search return photos that match the question? | Precision at 5 and at 10 | 7 |
| Is the first result right? | First-result accuracy | 7 |
| Which results are wrong, and why? | Incorrect retrievals, tagged by cause | 7, 9 |
| How fast is it? | Seconds per search; seconds per answer | 7 |
| Which approach works best? | All of the above, for each approach | 8 |
| Do the labels help? | Share of results whose review carries the asked-for sentiment, with and without the label filter | 8 |
| Do answers stay within the evidence? | Share of answer points supported by the items they cite | 6 |
| Does the answer admit when there's nothing to find? | "Not enough evidence" on questions with no relevant photos | 6 |
| Does it hold up on questions it has never seen? | The same measures on the fresh questions | Lesson from the revenue forecasting project |

## 2. The test questions

**25 test questions** (`evals/test_questions.csv`), written 23 Nov before any testing, in four groups:

| Group | Questions | What it tests |
|---|---|---|
| Visual | Q01–Q08 | Finding a kind of scene: pool, bathroom, buffet, lobby, sea view, balcony, restaurant, outside |
| The brief's examples | Q09–Q16 | The 8 example questions in the brief, word for word |
| Detail | Q17–Q22 | A topic with a sentiment, or a visual detail ("dirty or worn rooms") |
| Edge | Q23–Q25 | A broad question, and two with probably **nothing to find** (gym, spa) |

**10 fresh questions** (`evals/fresh_questions.csv`), written at the same time and **kept back**: run once, in Phase 7, after every choice is made. If they score much lower than the 25, the choices were tuned too closely to the 25.

Each question has a written rule for a relevant photo (`relevant_if`) and, where it applies, the review label it needs (`label_needed`).

## 3. What counts as relevant

The full rules are in `evals/relevance-guide.md`. In short, a result is relevant when **the photo** meets the question's rule, judged on the photo itself, **and** its **review** carries the label asked for (checked automatically from the source).

**Who judges the photos: Decision G, for approval:**

| Option | How | Effort and cost |
|---|---|---|
| A. Tez judges every result | About 700 photo judgements by eye | About 2–3 hours |
| **B. An AI judge, checked** (recommended) | Claude **Sonnet** 5.5 judges each photo against the rule, seeing **only the photo and the rule**: no description, score or review. Checked automatically against the dataset's own image labels where they apply (rooms, food, facilities, public areas); Tez can also judge a random 40 (about 10 minutes, optional) | About $1.50 |
| C. The dataset's image labels only | Free, automatic | Can't judge pools, bathrooms, views or dirt: too coarse |

A different model (Sonnet) judges than the one that wrote the descriptions (Opus), so caption search isn't marking its own homework. The judge is accepted if it agrees with the image labels, or with Tez, on at least **90%**.

## 4. Measures

| Measure | Definition |
|---|---|
| **Precision at 5 (P@5)** | Relevant results in the top 5, divided by 5. Averaged over questions. Also **P@10** |
| **First-result accuracy** | The share of questions whose first result is relevant (the brief's "retrieval accuracy") |
| **Incorrect retrievals** | Every result in the top 5 judged not relevant, listed with its question and approach |
| **Label accuracy** | The share of results whose review carries the asked-for label. 100% by design with the filter; measured **without** the filter to show what the labels add |
| **Search time** | Seconds from question to results, model already loaded; median and slowest |
| **Answer time and cost** | Seconds and dollars per answer, from the call log |
| **Grounded points** | The share of answer points whose cited items support them. Checked by the AI judge, with Tez reading 5 answers |
| **Honest gaps** | On Q24 and Q25, does the answer say there isn't enough evidence? |

## 5. What's compared (Step 8)

| Approach | The question's words against… | Model |
|---|---|---|
| **Image search** | the photo itself | CLIP; SigLIP |
| **Caption search** | Claude's description of the photo | CLIP's and SigLIP's text encoders |
| **Keyword search** | the description and key objects, by word overlap (BM25) | none |

That's 5 approaches on the same 25 questions, all using the label filter. Plus one extra run, **image search with SigLIP but no label filter**, to measure what the labels add. Answers are generated only for the chosen approach.

## 6. Pass marks

Set now, before testing. They apply to the approach chosen for the product.

| Measure | Pass mark | Applies to |
|---|---|---|
| P@5, average | **at least 0.80** | Q01–Q22 (the edge questions are excluded: two have nothing to find) |
| First-result accuracy | **at least 85%** | Q01–Q22 |
| Label accuracy with the filter | **100%** | Questions with a label |
| Search time | **under 2 seconds** (median) | All |
| Answer time | **under 15 seconds** (median) | All |
| Answer cost | **under $0.05** each | All |
| Grounded points | **at least 95%** supported; **no** point without a citation | All answers |
| Honest gaps | **2 of 2** | Q24, Q25 |
| Fresh questions | P@5 no more than **0.10 below** the test questions | F01–F10, Phase 7 |

**If a mark is missed:** it's reported as missed, with the reason, and the Product Owner decides whether to change something (through the change log) or accept it, as in the casino floor project.

## 7. Budget

| Item | Estimate |
|---|---|
| Spent so far | $4.95 |
| AI judge, 25 questions, 6 runs | about $1.50 |
| Answers for 25 questions, and checking them | about $0.90 |
| Fresh questions in Phase 7 | about $0.50 |
| **Total** | **about $7.85 of $10** |

## 8. Outputs

- `evals/results/`: per-question and per-approach tables, the comparison table (the brief's Step 8 table), the incorrect retrievals, and the answers.
- An experiment log entry for every run.
- The failure analysis (Step 9) uses the incorrect retrievals.
