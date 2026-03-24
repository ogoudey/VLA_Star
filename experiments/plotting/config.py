# ─────────────────────────────────────────────
#  config.py  –  all tuneable parameters
# ─────────────────────────────────────────────

# config.py
from presets import PRESETS

ACTIVE_PRESET = None # Look in presets. Set this variable

# ── Input files ───────────────────────────────
EXPERIMENT_CSV = "experiment.csv"   # timestamp_unix, playerX/Y/Z, robotX/Y/Z
GAME_CSV    = "game.csv"      # timestamp, type, description

# ── Output ────────────────────────────────────
OUTPUT_FILE   = "violin_plot.png"   # set to None to show interactively
DPI           = 150

# ── Violin shape ──────────────────────────────
# KDE bandwidth: 'scott' or 'silverman', or a float (smaller = more detail)
KDE_BANDWIDTH    = "scott"

# Maximum half-width of the violin in data-distance units.
# The violin is symmetric: it spans [-VIOLIN_MAX_WIDTH, +VIOLIN_MAX_WIDTH] on X.
# The X tick labels show absolute distances, not signed values.
VIOLIN_MAX_WIDTH = 5.0

# Number of points along the time axis used to evaluate the KDE shape.
KDE_N_POINTS = 300

# ── Axes ──────────────────────────────────────
X_LABEL = "X axis"
Y_LABEL = "Time from start (s)"
TITLE   = "HRI Experiment"

# ── Figure size ───────────────────────────────
FIGURE_WIDTH  = 6    # inches  (narrow — it's a single vertical violin)
FIGURE_HEIGHT = 10   # inches

# ── Violin style ──────────────────────────────
VIOLIN_COLOR       = "#4C9BE8"
VIOLIN_EDGE_COLOR  = "#1a1a2e"
VIOLIN_ALPHA       = 0.7

# Show median line?
SHOW_MEDIAN      = False
MEDIAN_COLOR     = "#ffffff"
MEDIAN_LINEWIDTH = 1.5

# ── Event annotation style ────────────────────
EVENT_COLORS = {
    "INTERACTION": "#FF6B6B",
    "EVENT":       "#FFD93D",
}
EVENT_COLOR_DEFAULT = "#aaaaaa"
SHOW_LEGEND = True

EVENT_LINE_ALPHA  = 0.85
EVENT_LINE_STYLE  = "--"
EVENT_LINE_WIDTH  = 1.4

EVENT_LABEL_FONTSIZE = 7
EVENT_LABEL_COLOR    = "#333333"

# Extra space to the right of the violin for event labels (in same units as VIOLIN_MAX_WIDTH)
EVENT_LABEL_X_MARGIN = 8.0

# ── Background / grid ─────────────────────────
BACKGROUND_COLOR = "#f8f9fa"
GRID_COLOR       = "#dddddd"
GRID_ALPHA       = 0.6

def apply_preset():
    globals().update(PRESETS.get(ACTIVE_PRESET, {}))