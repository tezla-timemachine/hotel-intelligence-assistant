# Changelog

## [0.7.1] — 2026-11-25 — View-only mode
- `VIEW_ONLY=1` starts the app for demos: search as usual, the answer button hidden, no calls to Claude (D22, CR-06).

## [0.7.0] — 2026-11-24 — Write-up
- Fresh test on 10 unseen questions: P@5 0.72, first result 90%, answers 95.7% backed (D20).
- Case study (09), limitations, README, HANDOVER.
- The annotated brief: "What we did" under every point of the brief.

## [0.6.0] — 2026-11-24 — App, failure analysis, UAT
- Failure analysis of all 36 wrong top-5 results, by the brief's five causes.
- Streamlit app: search, gallery, scores, labels, "photos like this", cited answer on a button.
- App searches sped up from about 2 s to 0.1–0.2 s (DF-10). Business UAT 12 of 12 (D18). Privacy note.

## [0.5.0] — 2026-11-23/24 — Evaluation and comparison
- 25 test questions, 6 approaches, 1,125 photo judgements by Claude Sonnet; image search with SigLIP chosen (P@5 0.81).
- Question rules fixed: plurals, more negative words, facility rooms (CR-04).
- Answers moved from Opus 5.5 to Sonnet 5.5 after a sample test (CR-05); cheapest-suitable-model rule (D16).

## [0.4.0] — 2026-11-23 — Search and answers
- Question rules, review-label filters, search by image, search log (D12).
- Grounded answers with citations (D13); evaluation plan (07) written before testing (D14).

## [0.3.0] — 2026-11-23 — Embeddings and database
- CLIP and SigLIP installed locally; six Chroma collections (D10, D11).

## [0.2.0] — 2026-11-23 — Image descriptions
- 501 images described by Claude Opus 5.5 in a fixed form (D8).

## [0.1.0] — 2026-11-23 — Data and documents
- ViMACSA downloaded; 501 images and 267 reviews selected; reviews translated (D2–D4).
- Documents 01–05, risk register (06), change log (10), fact sheet.
