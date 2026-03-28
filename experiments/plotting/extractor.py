#!/usr/bin/env python3
"""
Parses a directory of CSVs for game interaction outcomes and plots
a 2x2 payoff matrix showing probabilities of each result.

Usage: python plot_payoff.py [GAME_DIR]
"""

import os
import sys
import csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

GAME_DIR = sys.argv[1] if len(sys.argv) > 1 else "/home/olin/RobotInUnity/CastleGame/CastleGame_Data/Data"

OUTCOMES = {
    "both_won":   "closed - both won",
    "robot_only": "only robot reached goal",
    "player_only": "only player reached goal",
    # anything else → neither
}

counts = {k: 0 for k in OUTCOMES}
counts["neither"] = 0
total = 0

for fname in os.listdir(GAME_DIR):
    if not fname.endswith(".csv"):
        continue
    fpath = os.path.join(GAME_DIR, fname)
    with open(fpath, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        found = False
        for row in reader:
            if len(row) < 3:
                continue
            label = row[2].strip()
            if label == OUTCOMES["both_won"]:
                counts["both_won"] += 1
                found = True
                break
            elif label == OUTCOMES["robot_only"]:
                counts["robot_only"] += 1
                found = True
                break
            elif label == OUTCOMES["player_only"]:
                counts["player_only"] += 1
                found = True
                break
        if not found:
            counts["neither"] += 1
        total += 1

if total == 0:
    print("No INTERACTION rows found. Check GAME_DIR and CSV format.")
    sys.exit(1)

probs = {k: counts[k] / total for k in counts}

print(f"Total INTERACTION events: {total}")
for k, v in counts.items():
    print(f"  {k:12s}: {v:5d}  ({probs[k]:.1%})")

matrix = np.array([
    [probs["both_won"],   probs["player_only"]],
    [probs["robot_only"], probs["neither"]],
])

LABELS = [
    ["R/2, R/2", "R, -T"],
    ["-T, R", "-T, -T"],
]

col_labels = ["Player: YES", "Player: NO"]
row_labels = ["Robot: YES", "Robot: NO"]

fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(matrix, cmap="YlGn", vmin=0, vmax=1, aspect="auto")

ax.set_xticks([0, 1])
ax.set_yticks([0, 1])
ax.set_xticklabels(col_labels, fontsize=12)
ax.set_yticklabels(row_labels, fontsize=12)
ax.xaxis.set_label_position("top")
ax.xaxis.tick_top()

ax.set_xlabel("Player reached goal?", fontsize=13, labelpad=10)
ax.set_ylabel("Robot reached goal?", fontsize=13, labelpad=10)

for i in range(2):
    for j in range(2):
        p = matrix[i, j]
        n = counts[list(counts.keys())[i * 2 + j]]
        text_color = "white" if p > 0.55 else "black"
        ax.text(j, i, f"{p:.1%}\n(n={n})\n{LABELS[i][j]}",
                ha="center", va="center",
                fontsize=13, fontweight="bold", color=text_color)

cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("Probability", fontsize=11)

ax.set_title(f"General Payoff Matrix  (N={total})", fontsize=14, pad=18)

plt.tight_layout()
out_path = "payoff_matrix.png"
plt.savefig(out_path, dpi=150, bbox_inches="tight")
print(f"\nSaved → {out_path}")
#plt.show()
