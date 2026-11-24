# Product / Business Brief: Multimodal Hotel Intelligence Assistant

> **Status:** v1.0, approved by the Product Owner, 23 Nov 2026 (D7). Statements marked *(assumption)* are placeholders, to confirm with a real hotel group before any deployment.
> Sources: the Week 7 brief (`docs/week7-brief.md`), the dataset fact sheet (`docs/week7-dataset.md`), the plan (`docs/week7-plan.md`).

---

## 1. Problem

A hotel group collects thousands of guest reviews, many with photos. Managers want to know **what guests are unhappy or happy about, and see it**. Today *(assumption, typical of hotel groups)*:

- **Reviews are read one by one,** or skimmed as star ratings. Patterns across hundreds of reviews are missed.
- **Photos can't be searched.** A manager can't ask "show me rooms guests complained about".
- **The words and the pictures are kept apart.** A complaint about a dirty room and the photo of that room sit in different places, or the photo shows something else entirely.
- **Reviews come in several languages.** This dataset's are Vietnamese; the managers asking may not read them.

**Problem statement:** hotel managers can't quickly find and see the evidence behind guest feedback, so decisions about rooms, food and facilities rest on impressions rather than on what guests actually said and showed.

---

## 2. The product story

**The user:** a **hotel group quality or operations manager**, preparing a monthly review of guest feedback across hotels.

**The decision it supports:** **where to act first, with evidence.** Which part of the guest experience (rooms, food, facilities, public areas) draws the most complaints, what exactly guests say, and which photos show it. That feeds refurbishment priorities, supplier conversations and staff briefings. A marketing team can use the same search the other way: the facilities guests praise, with their photos.

**What changes for them:** instead of reading reviews and hunting for photos, they type *"room images associated with negative feedback"* and get, in seconds, the matching photos, the reviews behind them, and a short answer, *"most complaints are about smell and cleanliness…"*, with every point linked to its evidence.

**Why both images and text are needed:** in this dataset, of 101 images attached to reviews that complain about the **room**, only **52 actually show a room** (fact sheet, section 5). Searching the reviews alone returns the wrong pictures; searching the pictures alone misses what guests said. The product's job is to join the two.

---

## 3. Target users

| User | Role in the product | Priority |
|---|---|---|
| **Quality / operations manager** | Asks questions, reviews the evidence, decides where to act | **Primary** |
| Hotel general manager | Looks at their own hotel's complaints and praise | Secondary |
| Marketing manager | Finds the facilities and views guests praise, with photos | Secondary |
| Analyst | Checks search quality, cost and failures (evaluation and logs) | Secondary |

---

## 4. Current process *(assumption)*

1. Reviews are exported from booking sites into a spreadsheet, with star ratings.
2. An analyst reads a sample and tags themes by hand, monthly.
3. Photos are looked at separately, if at all.
4. Findings go into a slide deck, with a few quotes and the odd photo.

---

## 5. Is AI the right solution?

| Option | Good | Not so good | Verdict |
|---|---|---|---|
| Keyword search over reviews | Simple, cheap | Misses meaning ("smelled of smoke" ≠ "dirty"); can't search photos; one language only | Partial |
| A dashboard of the dataset's labels | Counts complaints by topic, no AI needed | Says nothing about **what** guests said or **what the photos show** | Useful alongside |
| **Multimodal search with RAG** | Finds photos and reviews by meaning; joins them; answers from the evidence | Must be measured: can return look-alike but wrong photos, or answers that go beyond the evidence | **Chosen, with evaluation** |

**Conclusion:** multimodal embeddings (CLIP, SigLIP) let a text question find photos by meaning, and RAG lets a model summarise only what was found. The dataset's own topic and sentiment labels cover "negative", "room" and "food" reliably, so the AI does what labels can't: understand the photos and the words.

---

## 6. Proposed AI opportunity

For each question, the system:
1. turns it into an **embedding** and finds the closest images, image descriptions and reviews in a **vector database**;
2. uses the source's **topic and sentiment labels** where the question asks for them ("negative", "food");
3. shows the **evidence**: images with a similarity score, and the reviews linked to them, in English with the Vietnamese original;
4. has **Claude write a short answer using only that evidence**, pointing to which images and reviews support each point, or saying there isn't enough evidence.

Prepared once: an **English translation** of each review (done) and a **short description and scene type** for each image (Phase 2), both tagged as generated.

**It never invents evidence.** Every answer is built from retrieved items only, and every generated field is tagged.

---

## 7. Business value and success measures

**What it costs to run** *(estimates; measured as we build)*:

| Item | Cost |
|---|---|
| Translating a review | $0.003 with Opus 5.5 (measured: $0.75 for 267); **about $0.0001 with Haiku 5.5**, which suits the job (D16) |
| Describing an image | $0.008 with Opus 5.5 (measured: $4.10 for 501); **about $0.004 with Sonnet 5.5** |
| Embeddings and search | **Free**, on this computer |
| One answered question | **$0.013 with Sonnet 5.5** (measured on 8 questions; Opus was $0.026) |

**Against today's process** *(assumption, to confirm with a real hotel group)*: a group receiving **1,000 reviews a month**, read at about a minute each, needs about **17 analyst hours a month** just to read them; at an assumed $40 an hour, about **$670 a month**, before finding any photos. Preparing the same 1,000 reviews and 2,000 photos for search would cost about **$8 a month** with right-sized models (translation with Haiku about $0.10, descriptions with Sonnet about $8), and each question about 1 cent. With Opus for everything it would be about $19. It doesn't replace the analyst: it gives them the evidence in seconds instead of hours.

**How the prototype is judged** (targets set in the evaluation plan, 07, before testing):

| Measure | What it checks |
|---|---|
| Precision at 5 and 10 | Of the top results, how many are actually relevant (judged by Tez, by eye) |
| Retrieval accuracy | The share of questions where a relevant result comes first |
| Incorrect retrievals | Every wrong result, and why (Step 9) |
| Response time | Search, and search plus answer |
| Grounded answers | Every claim in an answer is supported by the retrieved evidence |
| Cost per question | Within budget |

**In a real deployment (future, not measured here):** analyst hours saved, how often managers act on what they find, and whether complaint themes fall after action.

---

## 8. Scope

| | Version 1 (this project) | Future work |
|---|---|---|
| Data | ~500 images and their 267 reviews from ViMACSA | All 4,876 reviews; a real hotel group's reviews; new reviews as they arrive |
| Questions | English, typed in the app | Other languages; questions by uploading a photo |
| Search | Text to image, text to review, image descriptions, the dataset's labels | Per-hotel and per-date filters (not in the dataset) |
| Answers | Short, from retrieved evidence only, with citations | Monthly reports; trend charts |
| Runs | On this computer | Hosted, with sign-in |

---

## 9. Key assumptions to test

| # | Assumption | How | Status |
|---|---|---|---|
| A1 | CLIP or SigLIP can find the right hotel photos from an English question | Precision at K on test questions (Phase 5) | Open |
| A2 | Generated image descriptions make good search text | Caption search against image search (Step 8) | Open |
| A3 | The English translations keep the meaning | Spot-check | **Supported:** 9 of 9 checked kept the meaning (fact sheet) |
| A4 | The source's labels are reliable enough to filter on | Compare with what the photos show | Open. Known: images often don't show the complained-about topic |
| A5 | Answers can be kept to the evidence | Check every claim in test answers (Phase 5) | Open |
| A6 | Costs stay under $10 for the project | Every call logged | On track: $0.75 so far |

---

## 10. Stakeholders and decision rights

Roles are titles only. In this course project, Tez holds the Product Owner and Delivery Lead roles.

| Stakeholder | Interest | Decides |
|---|---|---|
| **Product Owner** (Tez) | A product that helps managers act on feedback | Scope, requirements, models, thresholds, approvals |
| **Delivery Lead** (Tez) | Building it well, on budget | Plan, method, relevance judgements in the evaluation |
| Claude (assistant) | Builds the system and drafts documents | Nothing on its own: proposes, explains, waits for a yes |
| Dataset authors | Research use of ViMACSA | Their terms: research only, cite the paper |
