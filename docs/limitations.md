# Limitations

**Status:** 24 Nov 2026. What this prototype can't show, and why. **A tested prototype and a starting point, not a system ready for a hotel group's real data.**

---

## 1. The data

| Limitation | Evidence | What it means |
|---|---|---|
| **Small selection** | 501 photos and 267 reviews out of 9,058 linked photos and 4,876 reviews | Some questions have fewer than 10 relevant photos (P@10 0.58 on the fresh questions) |
| **Negatives over-sampled** | 49% of selected reviews have a negative point; 20% in the dataset | Results describe search quality, not how guests feel overall |
| **No hotel names, dates or locations** | Not in the dataset | Can't filter by hotel or month, or show trends |
| **Photos resized to 512 × 512** | Every image | Some look squashed |
| **Research-use terms** | No open licence | Nothing from the dataset can be published or used commercially |
| **Reviews are translations** | Vietnamese, translated by Claude (spot-check of 9: meaning kept) | Nuance can be lost; the original is always shown |

## 2. The evaluation

| Limitation | Evidence | What it means |
|---|---|---|
| **An AI judged relevance** | Claude Sonnet, checked against the dataset's image labels: 87.7% agreement (mark 90%), the gap being definitions | One reader's rules; a person might judge borderline photos differently |
| **The answer checker is the same model as the answers** | Sonnet checked Sonnet's points | It may favour its own wording; Opus's answers were checked by the same checker |
| **35 questions** | 25 test, 10 fresh | Shows patterns, not precise rates |
| **One borderline photo** | A sitting area ranked first for every room question | First-result accuracy 77% on the test, 90% on the fresh questions |

## 3. The search

| Limitation | Evidence | What it means |
|---|---|---|
| **Can't see condition** | "Dirty or worn rooms": P@5 0 | Condition questions need the descriptions too (hybrid search, next step) |
| **Two things in one photo** | Bedrooms with a balcony 0; rooms with a city view 0.2 | Compound requests are weak |
| **Rules read the question** | 3 of 25 misread before CR-04; 10 of 10 fresh questions read correctly after | New wording can still be missed; Claude reading the question is the fallback (D12) |
| **Long texts cut off** | SigLIP reads 64 tokens: a third of descriptions and reviews cut | Affects caption search, not the chosen image search |
| **Scores aren't percentages** | SigLIP's best matches score about 0.1 | The app shows each score as a share of the best match |

## 4. The product

| Limitation | What it means |
|---|---|
| **English questions only** | Other languages would need translation or a multilingual model |
| **Runs on one Mac, no sign-in** | Real use needs hosting, access control and an access log (privacy note) |
| **Answers need the online API** | If credit runs out, search still works but answers don't (seen on 23 Nov) |
| **Faces in some photos** | Real use needs face blurring and consent (privacy note) |

## 5. What would make it a real system

1. A hotel group's own reviews and photos, with consent and the hotel's name and date on each.
2. Hybrid search for condition questions; two-part search for compound requests.
3. A person-judged evaluation on real questions from managers.
4. Hosting with sign-in, face blurring and a retention policy.
5. Cheaper preparation: Haiku for translation, Sonnet for descriptions.
