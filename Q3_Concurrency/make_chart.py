"""
STEP 6 - make_chart.py  -  graphs for the Q3 report (optional)
===============================================================
Run main.py (option 1) first: it saves experiment_results.csv and
timeline_last_round.csv. This file reads them and saves two pictures:

  rounds_chart.png    - time T of every round, with and without threads
  timeline_chart.png  - when each calculation ran in the last round (like the
                        t1 / t2 diagram in the brief)

Needs matplotlib (already installed for Q1).
"""

import csv
import os
import sys

import matplotlib.pyplot as plt

# The two CSV files only exist after main.py has run an experiment
for needed in ("experiment_results.csv", "timeline_last_round.csv"):
    if not os.path.exists(needed):
        print(f"{needed} not found.")
        print("Run main.py first and choose option 1 (or option 2), then run this file again.")
        sys.exit()

BLUE, ORANGE = "#2E74B5", "#C55A11"

# ---------------------------------------------------------------- chart 1
with open("experiment_results.csv") as f:
    rows = list(csv.DictReader(f))
rounds = [int(r["round"]) for r in rows]
with_t = [int(r["with_threads_ns"]) / 1e9 for r in rows]          # seconds, easier to read
without_t = [int(r["without_threads_ns"]) / 1e9 for r in rows]

plt.figure(figsize=(7, 3.6), dpi=200)
plt.plot(rounds, with_t, "o-", color=BLUE, label=f"With multithreading (avg {sum(with_t) / len(with_t):.2f} s)")
plt.plot(rounds, without_t, "s-", color=ORANGE,
         label=f"Without multithreading (avg {sum(without_t) / len(without_t):.2f} s)")
plt.ylim(0, max(with_t + without_t) * 1.2)
plt.xticks(rounds)
plt.xlabel("Round")
plt.ylabel("Time taken T (seconds)")
plt.grid(True, axis="y", alpha=0.3)
plt.legend(frameon=False, loc="lower right")
plt.gca().spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("rounds_chart.png")
print("Saved rounds_chart.png")

# ---------------------------------------------------------------- chart 2
with open("timeline_last_round.csv") as f:
    rows = list(csv.DictReader(f))

fig, axes = plt.subplots(2, 1, figsize=(7, 3.8), dpi=200, sharex=True)
for ax, mode, colour in zip(axes, ("with threads", "without threads"), (BLUE, ORANGE)):
    part = [r for r in rows if r["mode"] == mode]
    for i, r in enumerate(part):
        start, end = int(r["start_ns"]) / 1e9, int(r["end_ns"]) / 1e9
        ax.barh(i, end - start, left=start, color=colour, height=0.55)
        ax.text(end + 0.1, i, f"{end - start:.2f} s", va="center", fontsize=8)
    ax.set_yticks(range(len(part)), [f"Fib({r['n']})" for r in part])
    ax.invert_yaxis()
    total = max(int(r["end_ns"]) for r in part) / 1e9
    ax.set_title(f"{mode.capitalize()}:  T = {total:.2f} s", fontsize=10, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
axes[1].set_xlabel("Time since the first calculation started (seconds)")
plt.tight_layout()
plt.savefig("timeline_chart.png")
print("Saved timeline_chart.png")
