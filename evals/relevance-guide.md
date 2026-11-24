# Relevance guide: when is a search result relevant?

**What this is:** the written rules for judging each search result, so every judgement is made the same way, whether by Tez or by the AI judge (Decision G). Written 23 Nov 2026, before any test was run.

---

## 1. A result is relevant when both hold

1. **The photo** meets the question's rule in `relevant_if` (test question sheets). Judge **the photo itself**, never its description, its score or its review.
2. **The review's labels** include what the question asks for (`label_needed`), for example `Room_Negative`. This part is checked automatically from the source labels, so the judge only looks at the photo.

When `label_needed` is empty, only the photo counts.

## 2. Rules for the photo

| Situation | Judgement |
|---|---|
| The asked-for thing is the main subject | **Relevant** |
| It is clearly visible but not the main subject (a pool behind a restaurant terrace) | **Relevant** |
| It is barely visible, or you have to guess (a blur that might be a pool) | **Not relevant** |
| A **bathroom** when the question asks for a **room** | **Relevant**: bathrooms are part of the room (the dataset's Room topic) |
| A **view from a room** when the question asks for a **room** | **Not relevant**: the room itself must be shown |
| **Food on a table in a room** when the question asks for food | **Relevant** |
| "Dirty or worn" questions (Q17) | Relevant only if the dirt, stain, damage or wear **can be seen** |
| "Complains about" questions (Q23) | Relevant if the photo shows what the review complains about. The judge may read the review for this one question type |
| A collage or screenshot | Judge what it shows, by the same rules |

## 3. Metrics (evaluation plan 07, section 4)

- **Precision at 5 (P@5):** of the top 5 results, the share that are relevant. Also P@10.
- **First-result accuracy:** the share of questions whose first result is relevant.
- **Incorrect retrievals:** every result judged not relevant, listed for the failure analysis (Step 9).

## 4. Judging when there's nothing to find

For Q24 and Q25 there are probably no relevant photos. A search always returns *something*, so these will score low on P@5. That is expected: these questions test whether the **answer** says honestly that there isn't enough evidence.

## 5. Checking the judge

If the AI judge is used (Decision G, option B), Tez judges a random **40 of its judgements** by the same rules. The AI judge is accepted if it agrees on at least **90%**, and every disagreement is listed.
