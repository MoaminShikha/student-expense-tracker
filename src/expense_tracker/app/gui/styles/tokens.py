# The one place that holds all visual values in the app, changes are only done here
# Hex values are direct conversions of the HTML :root hsl() block.

from __future__ import annotations

# ── THEME CONTROL ─────────────────────────────────────────────────────────────
# Set DARK_MODE = True to switch all tokens to dark palette
DARK_MODE = False

# ── LIGHT THEME TOKENS ─────────────────────────────────────────────────────────
_LIGHT = {
    "BG": "#f7f3ec",          # hsl(36 25% 96%)   — warm cream body
    "PAPER_WARM": "#f3ede0",  # hsl(38 28% 94%)   — slightly deeper warm surface
    "SURFACE": "#ffffff",     # card / panel / topbar / sidebar background
    "HAIRLINE": "#e2dccd",    # hsl(36 16% 86%)   — standard border
    "HAIRLINE_S": "#cdc4ae",  # hsl(36 14% 76%)   — stronger border
    "FG": "#181a2c",          # hsl(240 28% 12%)  — primary text
    "MUTED_FG": "#475569",    # hsl(215 20% 32%)  — secondary text (improved contrast)
    "MUTED": "#838897",       # hsl(222 12% 55%)  — disabled / micro-labels
}

# ── DARK THEME TOKENS ──────────────────────────────────────────────────────────
_DARK = {
    "BG": "#020617",          # near-black background
    "PAPER_WARM": "#0f172a",  # slate-900
    "SURFACE": "#1e293b",     # slate-800
    "HAIRLINE": "#334155",    # slate-700
    "HAIRLINE_S": "#475569",  # slate-600
    "FG": "#f8fafc",          # near-white text
    "MUTED_FG": "#cbd5e1",    # slate-300
    "MUTED": "#94a3b8",       # slate-400
}

# ── APPLY THEME ────────────────────────────────────────────────────────────────
_theme = _DARK if DARK_MODE else _LIGHT

# ── BACKGROUND & SURFACE ──────────────────────────────────────────────────────
BG         = _theme["BG"]
PAPER_WARM = _theme["PAPER_WARM"]
SURFACE    = _theme["SURFACE"]
HAIRLINE   = _theme["HAIRLINE"]
HAIRLINE_S = _theme["HAIRLINE_S"]

# ── TEXT ──────────────────────────────────────────────────────────────────────
FG         = _theme["FG"]
MUTED_FG   = _theme["MUTED_FG"]
MUTED      = _theme["MUTED"]

# ── BRAND ─────────────────────────────────────────────────────────────────────
NAVY       = "#16172a"   # hsl(240 30% 11%)  — action buttons, avatar bg
GOLD       = "#c79a39"   # hsl(42 55% 50%)   — primary accent
GOLD_LEAF  = "#a87c24"   # hsl(42 65% 40%)   — spent figures, active text
FOCUS      = "#f1b619"   # hsl(42 90% 50%)   — focus ring

# ── SEMANTIC ──────────────────────────────────────────────────────────────────
RED        = "#962e2e"   # hsl(0 55% 38%)    — committed charges, crisis
GREEN      = "#22c55e"   # hsl(142 71% 45%)  — income, positive actions
GREEN_BG   = "#dff1ea" if not DARK_MODE else "#064e3b"   # green tinted background
AMBER      = "#f59e0b"   # hsl(38 92% 50%)   — caution / fuzzy charges
AMBER_BG   = "#fbeed4" if not DARK_MODE else "#7c2d12"   # amber tinted background
AMBER_BD   = "#dcb476"   # hsl(38 60% 70%)   — amber border

# ── HERO CARD STATES ──────────────────────────────────────────────────────────
HERO_OUTLINE_GREEN = GOLD          # on-track state border
HERO_OUTLINE_AMBER = AMBER         # caution state border
HERO_OUTLINE_RED   = RED           # crisis state border
HERO_BG1           = "#fbf7ea" if not DARK_MODE else "#0f172a"  # gradient start
HERO_BG2           = "#efe9da" if not DARK_MODE else "#1e293b"  # gradient end
# Note: HERO_TINT (rgba) lives in widgets/hero_card.py to avoid breaking hex-only token tests

# ── CATEGORY COLORS ───────────────────────────────────────────────────────────
CAT_FOOD   = "#ee6815"   # hsl(18 88% 50%)   — food / orange
CAT_EDU    = "#256de7"   # hsl(217 82% 52%)  — education / blue
CAT_TRANS  = "#199f6e"   # hsl(162 72% 36%)  — transport / teal
CAT_OTHER  = "#9456db"   # hsl(268 65% 58%)  — entertainment / other / purple
VIOLET     = "#713fc2"   # hsl(262 52% 50%)  — daily burn accent

# Keys match TransactionCategory.value exactly
CATEGORY_COLORS: dict[str, str] = {
    "food":          CAT_FOOD,
    "transport":     CAT_TRANS,
    "education":     CAT_EDU,
    "entertainment": CAT_OTHER,
    "other":         CAT_OTHER,
}

# ── TIMELINE ──────────────────────────────────────────────────────────────────
TRACK      = "#ece6da" if not DARK_MODE else "#334155"  # timeline background track

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
SIDEBAR_W    = 210
STAT_COL_W   = 290
CONTENT_PAD  = 24
CARD_RADIUS  = 14
PANEL_RADIUS = 14
HERO_RADIUS  = 14
TOPBAR_H     = 54
