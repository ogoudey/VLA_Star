"""
plot_violin.py
──────────────
Reads a positions CSV and an events CSV, then draws a single violin plot.

  Y axis  – elapsed time from start (seconds)
  X axis  – distance between player and robot (symmetric around 0)
  Events  – horizontal lines across the violin at the moment they occurred

All tuneable parameters live in config.py.
"""

import csv
import math
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from scipy.stats import gaussian_kde

import config as cfg

PRESET = None
# ─────────────────────────────────────────────────────────────
#  1.  Load data
# ─────────────────────────────────────────────────────────────

def load_positions(path):
    """Return list of (timestamp, distance) tuples."""
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = float(row["timestamp_unix"])
            dx = float(row["playerX"]) - float(row["robotX"])
            dy = float(row["playerY"]) - float(row["robotY"])
            dz = float(row["playerZ"]) - float(row["robotZ"])
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            rows.append((ts, dist))
    return rows


def load_events(path):
    """Return list of (timestamp, event_type, description) tuples."""
    events = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            keys = list(row.keys())
            ts    = float(row[keys[0]])
            etype = row[keys[1]].strip()
            desc  = row[keys[2]].strip()
            if etype in cfg.EVENT_COLORS:
                events.append((ts, etype, desc))
    return events


# ─────────────────────────────────────────────────────────────
#  2.  Build the violin shape manually
# ─────────────────────────────────────────────────────────────

def make_violin(elapsed_times, distances, n_points=200):
    """
    Compute a KDE of distances evaluated at n_points along the time axis.
    Returns:
        t_grid  - 1-D array of time values (y axis)
        half_w  - 1-D array of KDE widths  (half-width on each side of x=0)
    """
    if len(elapsed_times) < 2:
        sys.exit("Not enough position samples to draw a violin.")

    t_min, t_max = min(elapsed_times), max(elapsed_times)
    t_grid = np.linspace(t_min, t_max, n_points)

    # KDE over distance values, evaluated at each time grid point
    # We use a 2-D KDE: bandwidth over time selects nearby samples.
    kde = gaussian_kde(
        np.vstack([elapsed_times, distances]),
        bw_method=cfg.KDE_BANDWIDTH,
    )

    # For each time grid point, evaluate KDE marginalised over distance
    # by summing over a fine distance grid
    d_min, d_max = min(distances), max(distances)
    d_grid = np.linspace(d_min, d_max, 200)

    half_w = np.zeros(n_points)
    for i, t in enumerate(t_grid):
        vals = kde(np.vstack([np.full_like(d_grid, t), d_grid]))
        half_w[i] = vals.sum()

    # Normalise so the widest point equals VIOLIN_MAX_WIDTH
    max_w = half_w.max()
    if max_w > 0:
        half_w = half_w / max_w * cfg.VIOLIN_MAX_WIDTH

    return t_grid, half_w


# ─────────────────────────────────────────────────────────────
#  3.  Draw the plot
# ─────────────────────────────────────────────────────────────

def draw(positions, events):
    t_start = positions[0][0]
    elapsed = [ts - t_start for ts, _ in positions]
    dists   = [d for _, d in positions]

    t_grid, half_w = make_violin(elapsed, dists, n_points=cfg.KDE_N_POINTS)

    fig, ax = plt.subplots(figsize=(cfg.FIGURE_WIDTH, cfg.FIGURE_HEIGHT))
    fig.patch.set_facecolor(cfg.BACKGROUND_COLOR)
    ax.set_facecolor(cfg.BACKGROUND_COLOR)

    # ── Violin body ───────────────────────────────────────────
    ax.fill_betweenx(t_grid, -half_w, half_w,
                     color=cfg.VIOLIN_COLOR,
                     edgecolor=cfg.VIOLIN_EDGE_COLOR,
                     alpha=cfg.VIOLIN_ALPHA,
                     linewidth=1.2,
                     zorder=2)

    # ── Median line ───────────────────────────────────────────
    if cfg.SHOW_MEDIAN:
        median_dist = float(np.median(dists))
        # Find the half-width at the time closest to the overall median time
        median_t = float(np.median(elapsed))
        idx = int(np.argmin(np.abs(t_grid - median_t)))
        w   = half_w[idx]
        ax.hlines(median_t, -w, w,
                  colors=cfg.MEDIAN_COLOR,
                  linewidths=cfg.MEDIAN_LINEWIDTH,
                  zorder=4)

    # ── Event lines ───────────────────────────────────────────
    t_span = max(elapsed) - min(elapsed) or 1.0
    used_labels = set()

    for ts, etype, desc in events:
        ev_elapsed = ts - t_start
        color = cfg.EVENT_COLORS.get(etype, cfg.EVENT_COLOR_DEFAULT)

        # Find violin half-width at this time so the line spans the body
        idx = int(np.argmin(np.abs(t_grid - ev_elapsed)))
        w   = half_w[idx]

        ax.hlines(ev_elapsed, -w, w,
                  colors=color,
                  linestyles=cfg.EVENT_LINE_STYLE,
                  linewidths=cfg.EVENT_LINE_WIDTH,
                  alpha=cfg.EVENT_LINE_ALPHA,
                  zorder=3)

        # Label to the right of the violin
        ax.text(cfg.VIOLIN_MAX_WIDTH * 1.05, ev_elapsed, desc,
                fontsize=cfg.EVENT_LABEL_FONTSIZE,
                color=cfg.EVENT_LABEL_COLOR,
                va="center", ha="left",
                zorder=4)

        used_labels.add(etype)

    # ── Legend ────────────────────────────────────────────────
    legend_patches = [
        mpatches.Patch(
            color=cfg.EVENT_COLORS.get(et, cfg.EVENT_COLOR_DEFAULT),
            label=et, alpha=cfg.EVENT_LINE_ALPHA,
        )
        for et in used_labels
    ]
    if legend_patches and cfg.SHOW_LEGEND:
        ax.legend(handles=legend_patches, loc="upper left",
                  fontsize=8, framealpha=0.7)

    # ── Cosmetics ─────────────────────────────────────────────
    ax.set_xlabel(cfg.X_LABEL, fontsize=11)
    ax.set_ylabel(cfg.Y_LABEL, fontsize=11)
    ax.set_title(cfg.TITLE, fontsize=13, fontweight="bold")

    ax.grid(axis="y", color=cfg.GRID_COLOR, alpha=cfg.GRID_ALPHA, linewidth=0.8)
    ax.set_axisbelow(True)

    # X ticks: symmetric, labelled with positive distances only
    max_w = cfg.VIOLIN_MAX_WIDTH
    tick_positions = np.linspace(-max_w, max_w, 5)
    ax.set_xticks(tick_positions)
    ax.set_xticklabels([f"{abs(t):.1f}" for t in tick_positions])

    # Give a little right-margin room for event labels
    ax.set_xlim(-max_w * 1.1, max_w * 1.1 + cfg.EVENT_LABEL_X_MARGIN)

    plt.tight_layout()

    if cfg.OUTPUT_FILE:
        plt.savefig(cfg.OUTPUT_FILE, dpi=cfg.DPI, bbox_inches="tight")
        print(f"Saved → {cfg.OUTPUT_FILE}")
    else:
        plt.show()


# ─────────────────────────────────────────────────────────────
#  4.  Entry point
# ─────────────────────────────────────────────────────────────

def main():
    
    cfg.ACTIVE_PRESET = PRESET
    cfg.apply_preset() # Sets the config to a preset 
    print(f"Loading positions from  : {cfg.EXPERIMENT_CSV}")
    positions = load_positions(cfg.EXPERIMENT_CSV)
    print(f"  {len(positions)} rows loaded.")

    print(f"Loading events from     : {cfg.GAME_CSV}")
    events = load_events(cfg.GAME_CSV)
    print(f"  {len(events)} events loaded.")

    draw(positions, events)


if __name__ == "__main__":
    main()