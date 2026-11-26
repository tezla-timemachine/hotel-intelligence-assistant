"""Draws the two diagrams in docs/plan.md: how the system works, and the build order.

    python scripts/plan_diagrams.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "docs" / "diagrams"
NAVY, BLUE, PALE, GREY, AMBER, PALE_AMBER, GREEN, PALE_GREEN = "#1f3b57", "#2e75b6", "#eaf2fb", "#6b7280", "#b26b00", "#fdf3e1", "#2e7d32", "#e8f5e9"


def box(ax, x, y, w, h, title, sub="", fill=PALE, edge=BLUE):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fill, ec=edge, lw=1.4))
    ax.text(x + w / 2, y + h / 2 + (0.15 if sub else 0), title, ha="center", va="center", fontsize=10.5, color=NAVY, weight="bold")
    if sub:
        ax.text(x + w / 2, y + h / 2 - 0.2, sub, ha="center", va="center", fontsize=8.3, color=GREY, linespacing=1.3)


def arrow(ax, a, b, colour=BLUE):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=13, lw=1.4, color=colour))


def how_it_works():
    fig, ax = plt.subplots(figsize=(11.5, 5.6))
    ax.set_xlim(0, 11.5); ax.set_ylim(0, 5.6); ax.axis("off")
    w, h = 2.4, 1.1
    # top row: preparing the data, done once
    top = [("Images and reviews", "~500 images from ViMACSA,\neach linked to its review"),
           ("Vision model", "writes a short description\nand scene type per image"),
           ("Embedding model", "CLIP or SigLIP: images and\ntext become numbers"),
           ("Vector database", "Chroma: embeddings with\nimage, description, review")]
    xs = [0.1, 3.0, 5.9, 8.8]
    w = 2.4
    yt = 3.55
    for x, (t, s) in zip(xs, top):
        box(ax, x, yt, w, h, t, s)
    for i in range(3):
        arrow(ax, (xs[i] + w, yt + h / 2), (xs[i + 1], yt + h / 2))
    ax.text(0.1, 4.95, "Prepared once", fontsize=9, color=GREY, style="italic")
    # bottom row: answering a question, every time
    yb = 0.6
    bottom = [("Manager's question", "\"Show room images with\nnegative feedback\""),
              ("Search", "the question becomes numbers;\nthe closest records return"),
              ("Evidence", "top images, their reviews\nand similarity scores"),
              ("Answer", "Claude answers only from\nthe evidence, citing it")]
    fills = [(PALE_GREEN, GREEN), (PALE, BLUE), (PALE, BLUE), (PALE_AMBER, AMBER)]
    for x, (t, s), (f, e) in zip(xs, bottom, fills):
        box(ax, x, yb, w, h, t, s, fill=f, edge=e)
    for i in range(3):
        arrow(ax, (xs[i] + w, yb + h / 2), (xs[i + 1], yb + h / 2))
    arrow(ax, (xs[3] + w / 2, yt), (xs[1] + w / 2 + 0.3, yb + h), GREY)
    ax.text(5.2, 2.55, "search looks up\nthe database", fontsize=8, color=GREY, ha="center")
    ax.text(0.1, 2.0, "Every question", fontsize=9, color=GREY, style="italic")
    ax.text(5.75, 5.42, "How the system works", ha="center", fontsize=13, color=NAVY, weight="bold")
    ax.text(5.75, 5.15, "Retrieve the evidence first, then answer only from it (RAG). The manager sees the evidence and the answer together.",
            ha="center", fontsize=9, color=GREY)
    fig.savefig(OUT / "1_how_it_works.png", dpi=170, bbox_inches="tight"); plt.close(fig)


def build_order():
    fig, ax = plt.subplots(figsize=(14, 3.4))
    ax.set_xlim(0, 14); ax.set_ylim(0, 3.4); ax.axis("off")
    phases = [("1. Understand", "~500 images;\ndocs 01–05; risks", "Step 1"),
              ("2. Describe", "a description and\nscene type per image", "Step 2"),
              ("3. Embed", "CLIP and SigLIP;\nChroma database", "Steps 3–4"),
              ("4. Search", "plain-English search;\nevidence-based answers", "Steps 5–6"),
              ("5. Measure", "test questions, P@K;\nthree approaches", "Steps 7–8"),
              ("6. App", "failures explained;\nthe app; UAT", "Steps 9–10"),
              ("7. Write it up", "case study, README,\nbrief, GitHub", "Deliverables")]
    w, h, y = 1.75, 1.35, 1.1
    for i, (t, s, steps) in enumerate(phases):
        x = 0.05 + i * 1.98
        box(ax, x, y, w, h, t, s)
        ax.text(x + w / 2, y - 0.25, steps, ha="center", fontsize=8.5, color=BLUE)
        if i < len(phases) - 1:
            arrow(ax, (x + w, y + h / 2), (x + 1.98, y + h / 2))
    ax.text(7, 3.15, "The build order", ha="center", fontsize=13, color=NAVY, weight="bold")
    ax.text(7, 2.85, "Each phase ends with a short recap and your sign-off. The BAU documents are written as each phase needs them.",
            ha="center", fontsize=9, color=GREY)
    fig.savefig(OUT / "2_build_order.png", dpi=170, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    how_it_works()
    build_order()
    print("written:", ", ".join(p.name for p in sorted(OUT.glob("*.png"))))
