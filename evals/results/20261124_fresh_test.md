# Fresh test: 10 questions never used before (Phase 7)

**Why:** the 25 test questions were used to fix the question rules (CR-04) and to choose the approach, so they're no longer a fully fair test. These 10 questions (`evals/fresh_questions.csv`) were written on 23 Nov, at the same time as the 25, and kept back until now: no rule, prompt or setting was tuned on them. This is a lesson from the revenue forecasting project: check on data the project hasn't touched.

**What ran (D19):** the chosen approach only, image search with SigLIP and the review labels, top 10. The same judge as the test set (Claude Sonnet 5.5, prompt j1) for a fair comparison; answers by Claude Sonnet 5.5 (D16), with their points checked by prompt g1. Cost **$0.49** (judge $0.22, answers $0.13, checks $0.14).

---

## 1. Results against the test questions

| Measure | Test questions (Q01–Q22) | **Fresh questions (F01–F10)** | Mark | |
|---|---|---|---|---|
| P@5 | 0.81 | **0.72** | no more than 0.10 below the test | ✓ (0.09 below) |
| P@10 | 0.82 | 0.58 | reported | |
| First result right | 77% | **90%** | ≥ 85% | ✓ |
| Label accuracy with the filter | 100% | **100%** | 100% | ✓ |
| Search time (median) | 0.06 s | **0.13 s** | under 2 s | ✓ |
| Answer points backed by their evidence | 87.8% (Opus) | **95.7%** (Sonnet, 44 of 46) | ≥ 95% | ✓ |
| Points citing evidence | 115 of 115 | **46 of 46** | every point | ✓ |
| Answer time and cost | 7.4 s, $0.026 (Opus) | **5.4 s, $0.013** (Sonnet) | under 15 s, $0.05 | ✓ |

**The search holds up** on unseen questions, just inside the mark. **The answers improve** with Sonnet, and now meet the 95% grounding mark the Opus answers missed. **The question rules (CR-04)** read all 10 fresh questions correctly, including wording they weren't tuned on ("complained about", "praise", "children's").

## 2. Question by question

| Question | P@5 | What happened |
|---|---|---|
| F01 Corridors and hallways | 1.0 | |
| F02 Beds with towels arranged on them | 0.6 | Beds found; some without towels (a detail inside the photo) |
| F03 Rooftop bars and terraces | 0.6 | Ground-level terraces mixed in |
| F04 Bathrooms guests complained about | 0.8 | The same sitting-area photo as in the test set (DF-02) |
| F05 Breakfast from positive reviews | 1.0 | |
| F06 Children's pools or play areas | **0.2** | Only about 5 photos in the selection show children or play areas; children in ordinary pools came back. **The answer said so**: "no item shows a dedicated children's pool" |
| F07 The hotel at night | 0.8 | |
| F08 Pools from negative reviews | 1.0 | |
| F09 Rooms with a city view | **0.2** | Two things in one photo again (a room **and** a city view), as with "bedrooms with a balcony" (DF-08). The answer said only one item clearly showed it |
| F10 What guests praise about the staff | 1.0 | Staff and reception desks found; service praise from the labels |

## 3. What it confirms

1. **The design holds:** image search for what can be seen, the review labels for sentiment, answers that say what the evidence doesn't show.
2. **The known weak spot is real, not chance:** two-part requests (F09; Q06 in the test) and rare scenes (F06) score lowest. The improvements in the failure analysis (search each part; hybrid search) are the right next step.
3. **P@10 drops more than P@5 (0.58):** beyond the first five, the search runs out of good matches on narrow questions. With only 501 photos, some questions have fewer than 10 relevant ones.
4. **Sonnet was the right switch:** 95.7% of points backed, at half the cost of Opus.

**The two unsupported points:** one missed a detail in a photo (a person under the covers); one said a review never criticised the pool when it called the facilities "a bit poor" in general.
