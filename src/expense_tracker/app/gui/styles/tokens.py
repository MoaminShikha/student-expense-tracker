# The one place that holds all visual values in the app, changes are only done here
# Hex values are direct conversions of the HTML :root hsl() block.
# LIGHT theme is the default; DARK theme colors defined below.

from __future__ import annotations

# ── BACKGROUND & SURFACE ──────────────────────────────────────────────────────
BG         = "#f7f3ec"   # hsl(36 25% 96%)   — warm cream body
PAPER_WARM = "#f3ede0"   # hsl(38 28% 94%)   — slightly deeper warm surface
SURFACE    = "#ffffff"   # card / panel / topbar / sidebar background
HAIRLINE   = "#e2dccd"   # hsl(36 16% 86%)   — standard border
HAIRLINE_S = "#cdc4ae"   # hsl(36 14% 76%)   — stronger border

# ── TEXT ──────────────────────────────────────────────────────────────────────
FG         = "#181a2c"   # hsl(240 28% 12%)  — primary text
MUTED_FG   = "#56586c"   # hsl(224 14% 38%)  — secondary text
MUTED      = "#838897"   # hsl(222 12% 55%)  — disabled / micro-labels
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
AMBER      = "#a05712"   # hsl(32 80% 38%)   — caution / fuzzy charges
AMBER_BG   = "#fbeed4"   # hsl(38 78% 94%)   — amber tinted background
AMBER_BD   = "#dcb476"   # hsl(38 60% 70%)   — amber border

# ── HERO CARD STATES ──────────────────────────────────────────────────────────
HERO_OUTLINE_GREEN = GOLD          # on-track state border
HERO_OUTLINE_AMBER = AMBER         # caution state border
HERO_OUTLINE_RED   = RED           # crisis state border
HERO_BG1           = "#fbf7ea"     # hsl(42 60% 97%) — gradient start
HERO_BG2           = "#efe9da"     # hsl(36 35% 93%) — gradient end
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
TRACK      = "#ece6da"   # hsl(36 16% 92%)   — timeline background track

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
