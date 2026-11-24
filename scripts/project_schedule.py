"""The Week 7 task schedule and Gantt chart (project plan, 04 and 05).

    python scripts/project_schedule.py

Writes docs/hotel-intelligence-05-project-schedule.csv and docs/hotel-intelligence-05-gantt-chart.png.
Dates after today are a proposal; edit TASKS and re-run.
"""
import csv
import datetime as dt
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

DOCS = Path(__file__).resolve().parents[1] / "docs"
TODAY = dt.date(2026, 11, 24)
FIRST, LAST = dt.date(2026, 11, 23), dt.date(2026, 12, 2)
COLOURS = {"Done": "#2e7d32", "In progress": "#2e75b6", "Planned": "#9fb8d0"}

# (id, phase, task, start, end, status, depends on, brief steps / documents)
TASKS = [
    ("T01", "1 Understand", "Download, inspect and select ~500 images; fact sheet", "2026-11-23", "2026-11-23", "Done", "", "Step 1; D2, D3"),
    ("T02", "1 Understand", "Translate the reviews (Decision B)", "2026-11-23", "2026-11-23", "Done", "T01", "Step 1; D4"),
    ("T03", "1 Understand", "Documents 01-05, risk register (06), change log (10)", "2026-11-23", "2026-11-23", "Done", "T01", "01-06, 10"),
    ("T04", "2 Describe", "Choose the description model; try 10 images; describe all", "2026-11-23", "2026-11-23", "Done", "T03", "Step 2; Decision C"),
    ("T05", "3 Embed", "Install CLIP, SigLIP, Chroma; embed; build the database", "2026-11-23", "2026-11-23", "Done", "T04", "Steps 3-4; D, E"),
    ("T06", "4 Search", "Search, labels in search, search by image", "2026-11-23", "2026-11-23", "Done", "T05", "Step 5; Decision I"),
    ("T07", "4 Search", "Answers from evidence (RAG); evaluation plan (07)", "2026-11-23", "2026-11-23", "Done", "T06", "Step 6; 07; F"),
    ("T08", "5 Measure", "Test questions, relevance judgements, P@K", "2026-11-23", "2026-11-24", "Done", "T07", "Step 7; G"),
    ("T09", "5 Measure", "Compare caption, CLIP and SigLIP search", "2026-11-24", "2026-11-24", "Done", "T08", "Step 8"),
    ("T10", "6 App", "Failure analysis", "2026-11-24", "2026-11-24", "Done", "T09", "Step 9"),
    ("T11", "6 App", "Streamlit app; UAT (08); privacy note; risks signed off", "2026-11-24", "2026-11-24", "Done", "T07", "Step 10; 06, 08; H"),
    ("T12", "7 Write up", "Fresh test questions; case study (09); limitations", "2026-11-24", "2026-11-24", "Done", "T10 T11", "09"),
    ("T13", "7 Write up", "README, HANDOVER, annotated brief; GitHub", "2026-11-24", "2026-11-24", "Done", "T12", "Deliverables"),
]


def main():
    with (DOCS / "hotel-intelligence-05-project-schedule.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "phase", "task", "start", "end", "status", "depends_on", "covers"])
        w.writerows(TASKS)
    fig, ax = plt.subplots(figsize=(12, 5.4))
    for i, (tid, phase, task, start, end, status, *_ ) in enumerate(TASKS):
        s, e = dt.date.fromisoformat(start), dt.date.fromisoformat(end) + dt.timedelta(days=1)
        ax.barh(i, (e - s).days, left=mdates.date2num(s), color=COLOURS[status], height=0.6, edgecolor="white")
        ax.text(mdates.date2num(e) + 0.08, i, task, va="center", fontsize=8.2, color="#1f3b57")
    ax.set_yticks(range(len(TASKS)))
    ax.set_yticklabels([f"{t[0]}  {t[1]}" for t in TASKS], fontsize=8.2)
    ax.invert_yaxis()
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%a %d"))
    ax.set_xlim(mdates.date2num(FIRST) - 0.2, mdates.date2num(LAST + dt.timedelta(days=4)))
    ax.axvline(mdates.date2num(TODAY) + 0.5, color="#b26b00", lw=1.2, ls="--")
    ax.text(mdates.date2num(TODAY) + 0.55, -0.9, "today", color="#b26b00", fontsize=8)
    ax.grid(axis="x", alpha=0.25); ax.spines[["top", "right"]].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in COLOURS.values()]
    ax.legend(handles, COLOURS.keys(), loc="upper right", frameon=False, fontsize=8.5)
    ax.set_title("Week 7 schedule (dates after today are proposed)", fontsize=12, color="#1f3b57", loc="left")
    fig.tight_layout()
    fig.savefig(DOCS / "hotel-intelligence-05-gantt-chart.png", dpi=160); plt.close(fig)
    print("written: schedule CSV and Gantt chart")


if __name__ == "__main__":
    main()
