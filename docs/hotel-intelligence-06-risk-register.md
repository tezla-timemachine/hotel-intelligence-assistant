# Risk Register: Multimodal Hotel Intelligence Assistant

> **Status:** v1.0, signed off by the Product Owner at the end of Phase 6, 24 Nov 2026 (D19); started in Phase 1, 23 Nov 2026. Updated at the end of every phase with what we actually saw; signed off by the Product Owner in Phase 6. Likelihood and impact: Low, Medium, High. "Left over" is the risk after the protection.

---

## 1. Summary: likelihood and impact before protection

| | Low impact | Medium impact | High impact |
|---|---|---|---|
| **High likelihood** | | R-13 | R-03 |
| **Medium likelihood** | R-10, R-14 | R-01, R-05, R-06, R-07, R-09 | R-04, R-08 |
| **Low likelihood** | R-12 | R-02 | R-11 |

## 2. Register

| ID | Risk | Evidence so far | Protection | Likelihood | Impact | Left over | Owner |
|---|---|---|---|---|---|---|---|
| **R-01** | **Not enough disk space** for the models and data | 7.9 GB free at the start; zip 3.5 GB (deleted); software and models 3.1 GB against a 2.7 GB estimate; a duplicate model copy and pip's cache removed. 7.9 GB free after install | Zip deleted after selection (D2); sizes shown before every install; Moondream (1.6 GB) can be removed | Medium | Medium | Low | Delivery Lead |
| **R-02** | **The translation loses meaning** or softens complaints | 9 of 9 spot-checked kept meaning and tone (D4) | Original kept beside it; translation tagged; more spot-checks on negative reviews | Low | Medium | Low | Delivery Lead |
| **R-03** | **The image doesn't show what the review talks about** | Of 101 images from reviews negative about the room, only 52 show a room (fact sheet) | Search checks both the image and the review; labels shown in the app; a main theme of the failure analysis | High | High | **High** | Product Owner |
| **R-04** | **Look-alike but irrelevant images** are returned | 36 of 125 top-5 results wrong for SigLIP image search; e.g. balconies for "bedrooms with a balcony", city views for "sea views" | Labels used where asked; three approaches compared; failure analysis | Medium | High | Medium | Delivery Lead |
| **R-05** | **CLIP and SigLIP miss hotel-specific meaning** ("dirty", "noisy", "complaint" aren't visible things) | Confirmed: "dirty or worn rooms" P@5 0.0 with SigLIP; without labels only 47% of results match the asked-for sentiment | Sentiment comes from the source labels, not the image; caption and review search compared | Medium | Medium | Medium | Delivery Lead |
| **R-06** | **Generated descriptions are wrong** | 20 of 20 checked by eye were accurate; scene types agree with the source labels 86–92%. "Visible issues" can be minor or design choices, so they're never treated as complaints | Tried on 10 images first; checked on a sample; tagged as generated | Medium | Medium | Low | Delivery Lead |
| **R-07** | **Answers go beyond the evidence** | 87.8% of answer points fully supported (mark 95%); the rest mostly over-describe photos; none invents a complaint | Answer only from cited items; "not enough evidence"; every test answer checked | Medium | Medium | Medium | Product Owner |
| **R-08** | **The test set is too small or too easy** to show real quality; one person judges relevance | 20–30 questions planned | Written rules for relevance; a fresh question set kept back; results reported with their limits | Medium | High | Medium | Product Owner |
| **R-09** | **Costs exceed the budget** | Translation $0.75 (estimate $0.30); descriptions $4.10 (estimate $3.00). Spend $4.85 of $10 | Every call logged with cost; estimates use measured token rates; spend cap in each script | Medium | Medium | Low | Product Owner |
| **R-10** | **The selection isn't representative** | Negatives over-sampled on purpose: 49% against 20% in the dataset | Said plainly in every result: search quality, not guest opinion | Medium | Low | Low | Product Owner |
| **R-11** | **Dataset terms** are broken by publishing it | Terms: research use only, no open licence | Images, reviews and the database stay out of Git (`.gitignore`); README cites the paper | Low | High | Low | Product Owner |
| **R-13** | **Long texts are cut off** by the embedding models | SigLIP reads 64 tokens: 167 of 501 descriptions and 79 of 267 reviews are cut off; CLIP (77 tokens): 27 and 64 | Compared in Step 8; possible fix: split long texts into sentences and embed each | High | Medium | Medium | Delivery Lead |
| **R-14** | **Similarity scores are read as percentages or compared across models** | CLIP's best matches score about 0.30, SigLIP's about 0.10 | The app explains the score, or shows it rescaled within each search | Medium | Low | Low | Product Owner |
| **R-12** | **Personal data in photos** (guests' faces) | Confirmed: guests' faces are clearly visible in some photos. Descriptions checked on 20 photos: people only ever "a guest" or "a person" | Descriptions never describe people; photos not published; privacy note in Phase 6 | Low | Low | Low | Product Owner |

## 3. Top risks: why they matter

- **R-03, the image–review mismatch,** is the one risk already proven in the data. If the product ignores it, a manager would show a photo of a pool next to a complaint about a room. It shapes how search works (Decision I) and what the failure analysis looks for.
- **R-04 and R-05:** embeddings are strong at "what it looks like" and weak at "how the guest felt". That's why sentiment should come from the source labels.
- **R-08:** a small test set can make the results look better than they are. The fresh question set is the protection, learned from reviewer feedback on the revenue forecasting project.

## 4. Review log

| Date | Change |
|---|---|
| 23 Nov 2026 | Register started in Phase 1 with 12 risks (D1) |
| 23 Nov 2026 | End of Phase 2: R-06 and R-09 updated with evidence |
| 23 Nov 2026 | End of Phase 3: R-13 (text cut off) and R-14 (score scales) added |
| 24 Nov 2026 | Phase 5: R-04, R-05 and R-07 updated with evaluation evidence |
| 24 Nov 2026 | Phase 6: R-12 updated (faces confirmed; privacy note written); register ready for sign-off |
