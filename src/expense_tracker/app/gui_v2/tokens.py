from __future__ import annotations

# ── BACKGROUND & SURFACE ──────────────────────────────────────────────────────
BG         = "#f7f3ec"
PAPER_WARM = "#f3ede0"
SURFACE    = "#ffffff"
HAIRLINE   = "#e2dccd"
HAIRLINE_S = "#cdc4ae"

# ── TEXT ──────────────────────────────────────────────────────────────────────
FG         = "#181a2c"
MUTED_FG   = "#56586c"
MUTED      = "#838897"
DISABLED   = "#a8a8b8"

# ── BRAND ─────────────────────────────────────────────────────────────────────
NAVY       = "#16172a"
GOLD       = "#c79a39"
GOLD_LEAF  = "#a87c24"
FOCUS      = "#f1b619"

# ── SEMANTIC ──────────────────────────────────────────────────────────────────
RED        = "#962e2e"
GREEN      = "#1b6a4f"
GREEN_BG   = "#dff1ea"
AMBER      = "#a05712"
AMBER_BG   = "#fbeed4"
AMBER_BD   = "#dcb476"

# ── HERO CARD STATES ──────────────────────────────────────────────────────────
HERO_OUTLINE_GREEN = GOLD
HERO_OUTLINE_AMBER = AMBER
HERO_OUTLINE_RED   = RED
HERO_BG1           = "#fbf7ea"
HERO_BG2           = "#efe9da"

# ── CATEGORY COLORS ───────────────────────────────────────────────────────────
CAT_FOOD   = "#ee6815"
CAT_EDU    = "#256de7"
CAT_TRANS  = "#199f6e"
CAT_OTHER  = "#9456db"
VIOLET     = "#713fc2"

CATEGORY_COLORS: dict[str, str] = {
    "food":          CAT_FOOD,
    "transport":     CAT_TRANS,
    "education":     CAT_EDU,
    "entertainment": CAT_OTHER,
    "other":         CAT_OTHER,
}

# ── TIMELINE ──────────────────────────────────────────────────────────────────
TRACK = "#ece6da"

# ── TYPE SCALE (px) ───────────────────────────────────────────────────────────
T_MICRO = 8
T_MINI  = 9
T_XS    = 10
T_SM    = 11
T_BASE  = 12
T_MD    = 13
T_LG    = 15
T_XL    = 18

# ── LAYOUT ────────────────────────────────────────────────────────────────────
SIDEBAR_W   = 210
STAT_COL_W  = 290
CONTENT_PAD = 24
CARD_RADIUS = 14
PANEL_RADIUS = 14
HERO_RADIUS = 14
TOPBAR_H    = 54

# ── SPACING SCALE (dp/px) ─────────────────────────────────────────────────────
SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 16
SPACE_LG = 24
SPACE_XL = 32
