# Week 7 privacy and responsible use

**Status:** 24 Nov 2026. How the prototype treats guests' reviews and photos, what leaves this computer, and what a real hotel group would need to approve. **A prototype on a research dataset: not cleared for real guest data.**

---

## 1. What the system does, and doesn't

| The system **does** | The system **does not**, by design |
|---|---|
| Find hotel photos and reviews that match a question | Identify, name or track any guest |
| Describe **scenes**: rooms, pools, food, lobbies | Describe anyone's appearance, age, gender, ethnicity or clothing |
| Summarise what the retrieved reviews say, citing each | Add opinions or facts that aren't in the evidence |
| Show which fields are generated (translation, descriptions) | Present generated text as the guest's own words |

**How this is enforced:**
- **The description prompt** (d1) describes the scene and never the people: at most "a guest" or "a person". Checked on 20 photos by eye, including photos where guests' faces are clearly visible: no descriptions of people.
- **The answer prompt** (a1) forbids describing anyone and allows only cited evidence.
- **The original Vietnamese review** is always kept and shown beside the translation.

## 2. What data exists, and where

| Data | Where | Contains people? | Leaves this computer? |
|---|---|---|---|
| 501 photos and 267 reviews (ViMACSA, research use only) | `data/selected/` | **Yes: guests' faces in some photos**; reviews are personal opinions | Sent to Anthropic for translation (reviews), descriptions (photos), and answers (the 6 shown items), each step approved |
| Translations and descriptions | `data/selected/*.csv` | No personal details by design | No |
| Embeddings and the Chroma database | `models/`, `data/chroma/` | Numbers only, but linked to the photos and reviews | No: built and searched on this Mac |
| Search log and call log | `data/results/` | Questions asked; no personal data | No |
| API key | `.env` (only this Mac's user can read it; never in Git) | — | Only to Anthropic, to authenticate |

**Search itself never leaves the computer.** Only an **answer** sends data out: the 6 photos and reviews on screen, when the user clicks the button.

## 3. Publishing

The dataset's terms are **research use only**, with no open licence. So the photos, reviews, translations, descriptions and the database are **never published**: they're excluded from Git (`.gitignore`). GitHub gets code, results, documents and the paper's citation.

## 4. For a real hotel group

| Area | What would be needed |
|---|---|
| **Consent and terms** | Guest reviews and photos used under the review site's and the hotel's terms; guests told how reviews are analysed |
| **Faces** | Blur faces before storing or sending photos, or exclude photos with people |
| **Access** | Sign-in; managers see their own hotels; an access log |
| **Retention** | Photos and reviews kept only as long as the reviews are published; logs without personal data |
| **Online AI** | The legal team reviews the AI provider's terms; or use only local models for anything personal |
| **Approvals** | Privacy, legal, security and the hotel group's guest-experience owner |

Until these are in place, the system stays a **prototype on a research dataset**.
