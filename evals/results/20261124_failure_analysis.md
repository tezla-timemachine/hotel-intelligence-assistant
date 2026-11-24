# Failure analysis (Step 9)

**Scope:** the chosen approach (image search with SigLIP and the review labels, D17) on the 25 test questions: 36 wrong results in the top 5, every one with the judge's reason (`test_incorrect.csv`). Plus the answer points not backed by their evidence (`test_answer_checks.csv`), and the 3 question misreadings fixed in CR-04. No new model calls: everything here comes from the evaluation already run.

---

## 1. The wrong results, by the brief's five causes

| Brief's cause | Wrong results | Where | Example |
|---|---|---|---|
| **The embedding returned visually similar but irrelevant images** | 11 | Q06 (5), Q05 (2), Q10, Q14, Q11, Q15 | "Bedrooms with a balcony" → 5 balconies seen from outside or from the doorway, **no bedroom**. "Sea views" → a city street and buildings among pines |
| **The system misunderstood the relationship between text and image** | 5 | Q17 (5) | "Dirty or worn rooms" → plain, clean rooms. **Dirt and wear aren't something an embedding sees**: it matched "room", not "dirty" |
| **The review was unrelated to the image** | 5 | Q23 (5) | The review complains about staff, a missing lift or noisy guests; its photo shows a street, a lobby or a pool. Present in the source (fact sheet: 52 of 101 room-complaint photos show a room) |
| **The query was too broad, or there was nothing to find** | 10 (Q23's 5 are counted above, though it is also too broad) | Q24, Q25; also Q23 | "What do guests dislike most?" has no topic to look for. Gym and spa: **no such photos exist**, so any result is wrong; the answers said so |
| **The image was misunderstood** | 5 | Q09, Q12, Q13, Q20, Q22 | One sitting-area photo (TV, sofa, no bed) ranked first for every room question, and judged "not a bedroom" under our rule. A table of snacks taken for breakfast |

**Counts:** 36 wrong results; 10 of them on the two questions with nothing to find.

## 2. The most important failures, and possible improvements

| # | Failure | Why it matters | Possible improvement |
|---|---|---|---|
| 1 | **Visual details that embeddings can't see** (dirt, wear, damage): Q17 scored 0 | Complaints are often about condition, and that's what managers ask | **Hybrid search:** combine image similarity with keyword search on the descriptions' *visible issues* (keyword search scored 0.6 on Q17; image search 0). The descriptions already list stains and wear |
| 2 | **Two things in one photo** ("bedroom **with** a balcony"): Q06 scored 0 | Compound requests are natural for managers | Ask for both parts separately and keep photos that match both; or search the descriptions, which name both |
| 3 | **Photos that don't show what the review says** | A manager could show the wrong photo next to a complaint | Already handled in the answers: they say "the photos don't show the complaint" (Q09, Q11, Q15, Q17). The app should show this warning next to each result whose image topic differs from the review's complaint |
| 4 | **One borderline photo ranked first for every room question** | First-result accuracy fell from about 90% to 77% because of a single image | Agree the rule with users (is a sitting area "a room"?); or demote images whose source image topic doesn't match the question |
| 5 | **Broad questions** ("what do guests dislike most?") | Useful questions, but with no topic to search | Answer them from the **labels** (count complaints by topic) and then show photos for the top topic, rather than searching images directly |

## 3. Answer failures (Opus answers, 25 questions)

| Kind | Points | Example | Improvement |
|---|---|---|---|
| Over-describing photos | 10 | "Sun loungers and umbrellas" said of two pools when only one shows them; "patterned chairs" that are plain | A stricter prompt: mention a detail only if every cited photo shows it. **Sonnet 5.5 had none of these** on the 8-question sample (100% backed) |
| Generalising too far | 2 | "Room problems are the most repeated complaint" from two reviews | Prompt rule: no "most" or "main" without counting the evidence |
| Small mistakes in what a review says | 2 | Listing a complaint the cited review didn't make | Same stricter prompt |

**None invented a complaint**, and every point cited its evidence. The answers already help with failure 3: they told the manager when the photos didn't show the complaint.

## 4. The question rules (fixed, CR-04)

| Misreading | Cause | Fix |
|---|---|---|
| "bath**rooms**" not recognised | Plurals missing from the word lists | Plurals match automatically |
| "**dislike**" not seen as negative | Word missing | More negative words |
| "spa treatment **rooms**" read as guest rooms | "room" with a facility word | Room ignored when a facility word is present |

**Lesson:** rules are transparent and free, but brittle with new wording. The fresh questions (Phase 7) will show whether the fixes hold on wording they haven't seen.

## 5. What this means for the product

1. **Image search is right for "show me X"**, where X is something you can see: pools, rooms, food, lobbies (visual P@5 0.82).
2. **Sentiment must come from the reviews' labels**, never from the image.
3. **Condition questions need the descriptions too**: a hybrid of image and keyword search is the next improvement.
4. **The answer layer is where the image–review mismatch is explained to the manager**, and it does this well.
