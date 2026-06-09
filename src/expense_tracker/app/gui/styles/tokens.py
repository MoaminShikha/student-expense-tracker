# The one place that holds all visual values in the app, changes are only done here
# Hex values are direct conversions of the HTML :root hsl() block.
# LIGHT theme is the default; DARK theme colors defined below.

from __future__ import annotations

# ── THEME CONTROL ─────────────────────────────────────────────────────────────
# Set DARK_MODE = True to switch all tokens to dark palette
DARK_MODE = True

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
DISABLED   = "#a8a8b8"   # hsl(240 8% 68%)   — disabled interactive elements

# ── BRAND ─────────────────────────────────────────────────────────────────────
NAVY       = "#16172a"   # hsl(240 30% 11%)  — action buttons, avatar bg
GOLD       = "#c79a39"   # hsl(42 55% 50%)   — primary accent
GOLD_LEAF  = "#a87c24"   # hsl(42 65% 40%)   — spent figures, active text
FOCUS      = "#f1b619"   # hsl(42 90% 50%)   — focus ring

# ── SEMANTIC ──────────────────────────────────────────────────────────────────
RED        = "#962e2e"   # hsl(0 55% 38%)    — committed charges, crisis
GREEN      = "#1b6a4f"   # hsl(162 60% 26%)  — income, safe money
GREEN_BG   = "#dff1ea"   # hsl(162 45% 92%)  — green tinted background
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

# ── SPACING SCALE (dp/px) ────────────────────────────────────────────────────
SPACE_XS     = 4
SPACE_SM     = 8
SPACE_MD     = 16
SPACE_LG     = 24
SPACE_XL     = 32

# ── Z-INDEX SCALE ────────────────────────────────────────────────────────────
Z_BASE       = 0
Z_DROPDOWN   = 10
Z_STICKY     = 20
Z_MODAL      = 100
Z_TOAST      = 1000

# ── DARK MODE THEME ───────────────────────────────────────────────────────────
# Dark theme color overrides — use these when dark mode is enabled.
# Light mode is the current standard defined above.

DARK_BG              = "#1a1a2e"   # hsl(240 25% 12%) — dark background
DARK_PAPER_WARM      = "#242442"   # hsl(240 20% 16%) — slightly lighter surface
DARK_SURFACE         = "#2d2d47"   # hsl(240 18% 19%) — card/panel background
DARK_HAIRLINE        = "#3d3d57"   # hsl(240 15% 26%) — subtle dividers
DARK_HAIRLINE_S      = "#4d4d67"   # hsl(240 12% 33%) — stronger dividers
DARK_FG              = "#e8e8f0"   # hsl(240 12% 93%) — primary text
DARK_MUTED_FG        = "#a8a8b8"   # hsl(240 8% 68%)  — secondary text
DARK_MUTED           = "#767686"   # hsl(240 8% 53%)  — disabled / micro-labels
DARK_DISABLED        = "#535363"   # hsl(240 6% 38%)  — disabled interactive
DARK_RED             = "#ff6b6b"   # hsl(0 100% 68%)  — brighter red for dark
DARK_GREEN           = "#51cf66"   # hsl(135 70% 65%) — brighter green for dark
DARK_GOLD            = "#ffd93d"   # hsl(42 100% 65%) — brighter gold for dark
DARK_AMBER           = "#ffb347"   # hsl(32 100% 65%) — brighter amber for dark
DARK_GOLD_LEAF       = "#e6b800"   # hsl(42 100% 48%)  — darker gold for dark mode text
DARK_HERO_BG1        = "#2a2942"   # hsl(240 20% 20%)  — dark gradient start
DARK_HERO_BG2        = "#1f1f38"   # hsl(240 25% 15%)  — dark gradient end
DARK_TRACK           = "#3a3a52"   # hsl(240 15% 28%)  — dark timeline track
DARK_CAT_FOOD        = "#ff8c42"   # hsl(18 100% 60%)  — brighter food color
DARK_CAT_EDU         = "#5b9cff"   # hsl(217 100% 65%) — brighter education color
DARK_CAT_TRANS       = "#2dd4bf"   # hsl(162 100% 55%) — brighter transport color
DARK_CAT_OTHER       = "#c77dff"   # hsl(268 100% 68%) — brighter entertainment/other color
