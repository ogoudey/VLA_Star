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
from pathlib import Path

GAME_DIR = sys.argv[1] if len(sys.argv) > 1 else "/home/olin/RobotInUnity/CastleGame/CastleGame_Data/Data"
path_dir = Path(GAME_DIR)

FILE_NAME = path_dir.stem
OUTCOMES = {
    "both_won":   "closed - both won",
    "robot_won": "robot reached goal",
    "player_won": "player reached goal",
    # anything else → neither
}

counts = {k: 0 for k in OUTCOMES}
counts["neither"] = 0
total = 0
total_times = 0
for fname in os.listdir(GAME_DIR):
    if not fname.endswith(".csv"):
        continue
    fpath = os.path.join(GAME_DIR, fname)
    
    with open(fpath, newline="", encoding="utf-8", errors="replace") as f:
        print(f"New file: {fpath}")
        reader = csv.reader(f)
        player_won, robot_won, both_won = False, False, False
        is_legit_game_result = False
        start_time, end_time = None, None
        for row in reader:
            if len(row) < 3:
                continue
            try:
                ts = float(row[0].strip())
                if start_time is None:
                    start_time = ts
                end_time = ts
            except ValueError:
                pass
            label = row[2].strip()
            if label == OUTCOMES["both_won"]:
                print(f"\tFound: {label}")
                both_won = True
            elif label == OUTCOMES["robot_won"]:
                print(f"\tFound: {label}")
                robot_won = True
            elif label == OUTCOMES["player_won"]:
                print(f"\tFound: {label}")
                player_won = True
            elif label == "closed":
                is_legit_game_result = True
        if both_won:
            print(f"both_won")
            counts["both_won"] += 1
        elif player_won:
            print(f"player won")
            counts["player_won"] += 1
        elif robot_won:
            print(f"robot won")
            counts["robot_won"] += 1
        if is_legit_game_result:
            total += 1
            total_time = (end_time - start_time) if (start_time and end_time) else 0
            print(f"\tTotal interaction time: {total_time:.3f}s")
            total_times += total_time

if total == 0:
    print("No INTERACTION rows found. Check GAME_DIR and CSV format.")
    sys.exit(1)

probs = {k: counts[k] / total for k in counts}

print(f"Total interactions: {total}")
print(total_times)
average_time = total_times / total
print(f"Average interaction time: {average_time}")
for k, v in counts.items():
    print(f"  {k:12s}: {v:5d}  ({probs[k]:.1%})")

matrix = np.array([
    [probs["both_won"],   probs["player_won"]],
    [probs["robot_won"], probs["neither"]],
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
        if not n == 0:
            ax.text(j, i, f"{p:.1%}\n{round(average_time, 0)}s\n(n={n})\n{LABELS[i][j]}",
                ha="center", va="center",
                fontsize=13, fontweight="bold", color=text_color)
        else:
            ax.text(j, i, f"{p:.1%}\n(n={n})\n{LABELS[i][j]}",
                ha="center", va="center",
                fontsize=13, fontweight="bold", color=text_color)

cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("Probability", fontsize=11)

ax.set_title(f"{FILE_NAME}\n(N={total})", fontsize=14, pad=18)

plt.tight_layout()
out_path = FILE_NAME
plt.savefig(out_path, dpi=150, bbox_inches="tight")
print(f"\nSaved → {out_path}")
#plt.show()
