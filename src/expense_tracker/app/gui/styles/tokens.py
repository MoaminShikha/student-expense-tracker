from __future__ import annotations

# ── BACKGROUND & SURFACE ──────────────────────────────────────────────────────
BG         = "#f5f0e8"   # hsl(36,25%,96%)  — warm cream body
PAPER_WARM = "#f2ece0"   # hsl(38,28%,94%)  — slightly deeper warm surface
SURFACE    = "#ffffff"   # card / panel background
HAIRLINE   = "#ddd7cb"   # hsl(36,16%,86%)  — standard border
HAIRLINE_S = "#c9c0b0"   # hsl(36,14%,76%)  — stronger border

# ── TEXT ──────────────────────────────────────────────────────────────────────
FG         = "#17172b"   # hsl(240,28%,12%) — primary text
MUTED_FG   = "#535971"   # hsl(224,14%,38%) — secondary text
MUTED      = "#7f8499"   # hsl(222,12%,55%) — disabled / micro-labels

# ── BRAND ─────────────────────────────────────────────────────────────────────
NAVY       = "#16162a"   # hsl(240,30%,11%) — sidebar background
GOLD       = "#c8962a"   # hsl(42,55%,50%)  — primary accent
GOLD_LEAF  = "#a07020"   # hsl(42,65%,40%)  — spent figures, active text

# ── SEMANTIC ──────────────────────────────────────────────────────────────────
RED        = "#8f2a2a"   # hsl(0,55%,38%)   — committed charges, crisis
GREEN      = "#1b6b46"   # hsl(162,60%,26%) — income, safe money
GREEN_BG   = "#e5f5ed"   # hsl(162,45%,92%) — green tinted background
AMBER      = "#9e4a0a"   # hsl(32,80%,38%)  — caution / fuzzy charges
AMBER_BG   = "#fdf3e3"   # hsl(38,78%,94%)  — amber tinted background
AMBER_BD   = "#e8c57a"   # hsl(38,60%,70%)  — amber border

# ── HERO CARD STATES ──────────────────────────────────────────────────────────
HERO_OUTLINE_GREEN = "#c8962a"   # GOLD
HERO_OUTLINE_AMBER = "#b05a10"   # deep amber
HERO_OUTLINE_RED   = "#8f2a2a"   # RED

# ── CATEGORY COLORS ───────────────────────────────────────────────────────────
CAT_FOOD   = "#e85d10"   # hsl(18,88%,50%)  — food / orange
CAT_EDU    = "#2563eb"   # hsl(217,82%,52%) — education / blue
CAT_TRANS  = "#1b8a60"   # hsl(162,72%,36%) — transport / teal
CAT_OTHER  = "#8b44d6"   # hsl(268,65%,58%) — entertainment / other / purple

CATEGORY_COLORS: dict[str, str] = {
    "food":          CAT_FOOD,
    "transport":     CAT_TRANS,
    "education":     CAT_EDU,
    "entertainment": CAT_OTHER,
    "other":         CAT_OTHER,
}

# ── TIMELINE ──────────────────────────────────────────────────────────────────
TRACK_BG   = "#ede8e0"   # hsl(36,16%,92%)  — timeline background track

# ── LAYOUT ────────────────────────────────────────────────────────────────────
SIDEBAR_W    = 210
STAT_COL_W   = 290
CONTENT_PAD  = 24
CARD_RADIUS  = 14
TOPBAR_H     = 54
