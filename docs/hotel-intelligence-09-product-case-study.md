# Case Study: Multimodal Hotel Intelligence Assistant

**23–24 November 2026.** A prototype that lets a hotel manager search guest photos and reviews together in plain English, and get an answer built only from the evidence. Built and evaluated as an AI product, one phase at a time. Tez was Product Owner and Delivery Lead, with Claude building the system and drafting the documents.

---

## 1. Problem

Hotel groups collect thousands of guest reviews with photos. Managers read reviews one by one and can't search the photos at all, so decisions about rooms, food and facilities rest on impressions. The question: **can AI find the evidence behind guest feedback, words and pictures together, and summarise it honestly?**

## 2. User and the decision it supports

The **quality or operations manager** preparing a monthly feedback review. The decision: **where to act first, with evidence**: which part of the stay draws complaints, what guests say, and which photos show it.

## 3. AI opportunity

Three kinds of AI, each doing what it's good at:
- a **vision language model** describes each photo;
- **multimodal embeddings** (CLIP, SigLIP) put photos and text in one space, so a sentence can find a picture;
- a **language model** answers only from what was retrieved (**RAG**).

The dataset's own topic and sentiment labels cover what images can't show: how the guest felt.

## 4. The key finding that shaped the product

In the source data, of 101 photos attached to reviews complaining about the **room**, only **52 actually show a room**. Searching reviews alone gives the wrong pictures; searching pictures alone misses what guests said. **The product's job is to join the two**, and to say when they don't match.

## 5. Product decisions

| Decision | Choice | Why |
|---|---|---|
| Data (D2, D3) | 501 images, 267 reviews; negatives over-sampled (49% against 20%) | The brief's questions are mostly about complaints; research-only terms, so nothing published |
| Language (D4) | Vietnamese reviews translated, original kept, tagged as generated | Managers read English; CLIP and SigLIP work best in English |
| Reading a question (D12) | Rules: topic and sentiment words become filters on the **review labels**; the rest is matched against the **photo** | Photos can't show sentiment; free, instant and transparent |
| Search (D17) | **Image search with SigLIP**, plus the labels | Best in the comparison (P@5 0.81) |
| Answers (D16) | **Claude Sonnet 5.5** with the photos, citing every point | Better grounded than Opus on a sample (100% against 78%), at half the cost |
| Cost of an answer | On a button, about 1 cent | Searching is free; spending only when asked |

## 6. Architecture

Prepared once: select → translate → describe → embed (CLIP, SigLIP, on this Mac) → Chroma database (six collections, each record linked to its photo, description, review and labels).
Every question: read by rules → filter on the review labels → rank photos by similarity → show the evidence → on request, Claude answers from it. **Only translation, descriptions and answers leave the computer.**

## 7. Prototype

A Streamlit app: question box; "understood as" (topic, sentiment, what it looked for); a gallery of photos with match scores, label badges and the English review; the original Vietnamese and the generated description on request; "photos like this one"; a warning when a photo's own label differs from the question; and a cited answer on a button.

## 8. Evaluation

- **25 test questions** and **10 fresh questions** kept back, all written before testing, with written relevance rules (07).
- **1,225 photo judgements** by an AI judge (Claude Sonnet) that saw only the photo and the rule, checked against the dataset's own image labels.
- **Six approaches compared** on the same questions.

| Approach | P@5 | P@10 | First result |
|---|---|---|---|
| **Image search, SigLIP + labels** | **0.81** | **0.82** | 77% |
| Image search, CLIP + labels | 0.80 | 0.73 | 77% |
| Keyword search on descriptions | 0.63 | 0.61 | 68% |
| Caption search (SigLIP / CLIP text) | 0.53 / 0.47 | 0.48 / 0.47 | 45% / 59% |
| Image search, SigLIP, **no labels** | 0.54 | 0.53 | 50%; only **47%** of results from reviews with the right sentiment |

**Fresh questions:** P@5 0.72 (within 0.10 of the test, as required), first result 90%, labels 100%.
**Answers:** Sonnet 95.7% of points backed by their cited evidence on the fresh questions (mark 95%); every point cited; "not enough evidence" on both questions with nothing to find.
**UAT:** 12 of 12 business tests passed.

## 9. What failed

- **Things embeddings can't see:** "dirty or worn rooms" scored 0; dirt isn't visual similarity.
- **Two things in one photo:** "bedrooms with a balcony" and "rooms with a city view" scored 0 and 0.2.
- **The question rules misread 3 of 25 questions** at first ("bathrooms", "dislike", "spa treatment rooms").
- **Opus answers over-described photos:** 87.8% of points backed, short of the 95% mark.
- **The account ran out of credit:** 25 answer calls refused.
- **Searches in the app took 2 s** instead of 0.06 s, found in UAT.
- **The most expensive model by default:** Opus was used for translation, descriptions and answers without trying cheaper models. About **$3 more than needed**.

## 10. What changed because of it

| Failure | Change |
|---|---|
| Rule misreadings | Plurals, more negative words, facility rooms (CR-04); the fresh questions then all read correctly |
| Opus over-describing | Answers moved to Sonnet (CR-05): 95.7% backed, half the cost |
| Default to the dearest model | Rule: cheapest suitable model first, tested on a sample, dearer only with evidence (D16) |
| Credit outage | Scripts stop at the first refusal; every refusal logged at $0 |
| Slow app searches | One PyTorch thread for the question; models warmed at start (DF-10) |
| Photos that don't show the complaint | A warning in the app; answers say so |

## 11. Results

| Measure | Result |
|---|---|
| P@5, test / fresh | **0.81 / 0.72** |
| Label accuracy | **100%** |
| Search time | **0.1–0.2 s** in the app |
| Answers backed by evidence | **95.7%** (Sonnet, fresh questions) |
| Cost per answer | **$0.013** |
| Business UAT | **12 of 12** |
| Total spend | **$9.24 of $10** |

## 12. Next iteration

1. **Hybrid search:** combine image similarity with keyword search on the descriptions' visible issues, for condition questions.
2. **Two-part questions:** search each part and keep photos matching both.
3. **Broad questions** ("what do guests dislike most?"): count complaints from the labels first, then show photos for the top topic.
4. **Cheaper preparation:** Haiku for translation, Sonnet for descriptions (about $8 a month for 1,000 reviews and 2,000 photos).
5. **Real data:** a hotel group's own reviews, with consent, face blurring and sign-in.

## What I'd tell another PM

- **Join the modalities on purpose.** Half the "room complaint" photos didn't show a room: the value was in combining what the photo shows with what the guest said.
- **Let labels do what images can't.** Sentiment isn't visible; without the labels, half the results came from the wrong reviews.
- **Choose the cheapest model that fits, and test it.** Sonnet beat Opus on answers at half the price; Haiku was enough for translation.
- **Keep a fresh test set.** The 10 unseen questions confirmed the design and exposed the same weak spots as the failure analysis.
- **Spend only on request.** Search is free; the answer costs money, so it's a button.
