# Mizān — GUI Design File
> Version 1.0 · 2026-06-10
> Source of truth for the complete GUI rebuild. Every visual decision is made here. Implementation follows this file, not the other way around.

---

## 1. Overview

Mizān is a student cash-flow visibility tool. The GUI must communicate one thing instantly: **how much is safe to spend right now.** Everything else is secondary.

**Design character:** Quiet editorial. Warm, not cold. Precise, not flashy. The visual language borrows from print finance — serif numerals, monospaced labels, warm cream paper — not from generic fintech apps.

**Primary reference:** `Docs/visuals/mizan_dashboard.html` — treat it as the gold standard for visual appearance.

---

## 2. Design Tokens

All values live here. Implementation reads from this section only.

### 2.1 Color Palette

#### Light Theme (default — only theme for now)

| Token | Hex | Role |
|---|---|---|
| `BG` | `#f7f3ec` | App background (warm cream) |
| `PAPER_WARM` | `#f3ede0` | Slightly deeper warm surface (streak box, panel accents) |
| `SURFACE` | `#ffffff` | Cards, sidebar, topbar background |
| `HAIRLINE` | `#e2dccd` | Standard borders and dividers |
| `HAIRLINE_S` | `#cdc4ae` | Stronger borders |
| `FG` | `#181a2c` | Primary text (near-black navy) |
| `MUTED_FG` | `#475569` | Secondary text (improved contrast, min 4.5:1) |
| `MUTED` | `#838897` | Disabled, micro-labels, metadata |
| `DISABLED` | `#a8a8b8` | Disabled interactive elements |

#### Brand

| Token | Hex | Role |
|---|---|---|
| `NAVY` | `#16172a` | Action buttons, avatar background |
| `GOLD` | `#c79a39` | Primary accent, active nav border, decorative dots |
| `GOLD_LEAF` | `#a87c24` | Spent figures, active text, links |
| `FOCUS` | `#f1b619` | Focus rings (keyboard navigation) |

#### Semantic

| Token | Hex | Role |
|---|---|---|
| `RED` | `#962e2e` | Committed charges, crisis state |
| `GREEN` | `#1b6a4f` | Income, safe money |
| `GREEN_BG` | `#dff1ea` | Green-tinted backgrounds |
| `AMBER` | `#f59e0b` | Caution state, fuzzy charges |
| `AMBER_BG` | `#fbeed4` | Amber-tinted backgrounds |
| `AMBER_BD` | `#dcb476` | Amber borders |

#### Category Colors

| Token | Hex | Category |
|---|---|---|
| `CAT_FOOD` | `#ee6815` | Food |
| `CAT_EDU` | `#256de7` | Education |
| `CAT_TRANS` | `#199f6e` | Transport |
| `CAT_OTHER` | `#9456db` | Entertainment / Other |

#### Timeline / Hero States

| Token | Value | Role |
|---|---|---|
| `TRACK` | `#ece6da` | Timeline background track |
| `HERO_BG1` | `#fbf7ea` | Hero card gradient start |
| `HERO_BG2` | `#efe9da` | Hero card gradient end |
| `HERO_TINT` | `rgba(252,247,234,0.24)` | Hero card radial tint overlay |

### 2.2 Typography

Three fonts — each with a strict role. Never mix roles.

| Font | Weight | Role |
|---|---|---|
| **Playfair Display** | 700, 900 | All monetary values, large numbers, section headings |
| **DM Mono** | 400, 500 | Navigation labels, data labels, buttons, metadata |
| **Noto Naskh Arabic** | 400, 700 | Brand wordmark (מִיזָן / ميزان) only |

**Type scale (px):**

| Token | px | Usage |
|---|---|---|
| `T_MICRO` | 10 | Letter-spaced uppercase labels (e.g. "FREE MONEY") |
| `T_MINI` | 11 | Secondary micro-text, dates, sub-labels |
| `T_XS` | 11 | Caption text |
| `T_SM` | 11 | Standard body text in panels |
| `T_BASE` | 12 | Default body / nav items |
| `T_MD` | 13 | Topbar values, stat sub-values |
| `T_LG` | 15 | Stat card secondary numbers |
| `T_XL` | 18 | Section titles |
| `MONEY_SM` | 28px | Stat card main figures |
| `MONEY_MD` | 52px | Hero card free money display |

**Letter spacing rules:**
- ALL_CAPS micro labels: `0.18em`
- Nav items: `0.03em`
- Status badges: `0.10em`
- Monetary symbols (₪ italic): `opacity 0.38–0.45`

### 2.3 Layout

| Token | Value | Usage |
|---|---|---|
| `SIDEBAR_W` | 210px | Sidebar fixed width |
| `STAT_COL_W` | 290px | Stat column fixed width |
| `TOPBAR_H` | 54px | Topbar height (sticky) |
| `CONTENT_PAD` | 24px | Horizontal content padding |
| `CARD_RADIUS` | 14px | Cards and panels |
| `PANEL_RADIUS` | 14px | Bottom panels |
| `HERO_RADIUS` | 14px | Hero card |

### 2.4 Spacing Scale

| Token | px |
|---|---|
| `SPACE_XS` | 4 |
| `SPACE_SM` | 8 |
| `SPACE_MD` | 16 |
| `SPACE_LG` | 24 |
| `SPACE_XL` | 32 |

### 2.5 Z-Index Scale

| Token | Value | Usage |
|---|---|---|
| `Z_BASE` | 0 | Normal content |
| `Z_DROPDOWN` | 10 | Topbar (sticky) |
| `Z_STICKY` | 20 | Overlapping elements |
| `Z_MODAL` | 100 | Dialogs |
| `Z_TOAST` | 1000 | Toast notifications |

### 2.6 Shadows

Cards use **inset box-shadow** not drop-shadow:
- Standard card: `inset 0 0 0 1px HAIRLINE`
- Elevated dialog: `0 8px 32px rgba(24,26,44,0.12)`
- Tooltip: `0 4px 12px rgba(24,26,44,0.18)`

### 2.7 Dot-Grain Texture

Applied to: app background body, hero card interior
```
radial-gradient(rgba(120,110,90,0.08) 1px, transparent 1px)
background-size: 3px 3px
```

---

## 3. Component Inventory

### 3.1 Sidebar

**Fixed left column, 210px wide, full viewport height, sticky.**

#### Structure (top to bottom):
1. **Brand block** (padded 18px 20px 14px, bottom hairline divider)
   - Top row: `STUDENT BUDGET` micro-label (left) + version tag (right)
   - Wordmark: Arabic script "ميزان" in Noto Naskh Arabic, 25px, `GOLD_LEAF` color, RTL
   - Sub row: `MIZAN` monospace label (left) + session date range (right)

2. **Navigation** (flex:1, 8px vertical padding)
   - Section header: "MAIN" micro-label, 9px, `MUTED`, `0.18em` letter-spacing
   - Nav items (height 33px, padding 0 12px 0 18px):
     - Left: 2px solid border (transparent when inactive, `GOLD` when active)
     - Icon (16px SVG, `MUTED` inactive / `FG` active)
     - Label: DM Mono, `T_SM`, `MUTED_FG` inactive / `FG` active
     - Right dot: 4px circle `GOLD` (active item only)
     - Hover: `hsl(36 20% 95% / 0.7)` background, `FG` text
     - Active: `hsl(36 20% 94%)` background, `GOLD` left border
     - Transition: 120ms background + color + border-color

   **Pages:**
   - Dashboard (grid/layout icon)
   - Activity (list icon)
   - Insights (chart icon)
   - Settings (gear icon)

3. **Streak box** (margin 6px 14px, border-radius 10px, `PAPER_WARM` background)
   - Header row: "STREAK" micro-label (left) + count with unit (right)
   - Count: Playfair Display, `T_LG`, bold
   - 7 segment bars (4px height, `GOLD` = active, `HAIRLINE` = inactive)

4. **User block** (12px 20px padding, top hairline divider)
   - Avatar: 33px circle, `NAVY` background, `GOLD` initials, `T_XS`
     - Green online dot: 9px, bottom-right of avatar, `GREEN` fill, 2px `SURFACE` border
   - Name: `T_SM`, `FG`
   - Sub-label: `T_MINI`, `MUTED` (e.g. "Academic Year 2025–26")

---

### 3.2 Topbar

**Sticky top, 54px height, `SURFACE` background, bottom hairline divider.**

#### Left side:
- **Breadcrumb block**
  - Top: section label, `T_MINI`, `MUTED`, letter-spaced uppercase
  - Bottom: current date, `T_MD`, `FG`, weight 500

- **Sparkline block** (displayed only on Dashboard)
  - Mini label: "THIS MONTH", `T_MICRO`, `MUTED`
  - Value: Playfair Display, `T_MD`, bold, `FG`
  - Italic ₪ symbol at 45% opacity

#### Right side (margin-left: auto):
- **Period selector pill** (border: 1px `HAIRLINE`, border-radius: 999px, overflow hidden)
  - Segments: "Week" / "Month" / "Year" in DM Mono, `T_XS`
  - Active segment: `PAPER_WARM` background, `FG` color, weight 500
  - Inactive: transparent, `MUTED_FG`

- **Status pill** (border-radius 999px, 4px 12px padding, 1px border)
  - Three states:
    - `green`: `GREEN_BG` background, `hsl(162 40% 76%)` border, `GREEN` text
    - `amber`: `AMBER_BG` background, `AMBER_BD` border, `AMBER` text
    - `red`: `hsl(0 55% 94%)` background, `hsl(0 55% 70%)` border, `RED` text
  - Contains: SVG icon (11px) + pulse dot (7px animated circle) + label text
  - Pulse animation: `box-shadow` 0→4px→0, 2.4s ease-out infinite
  - Text: `T_XS`, weight 500, `0.07em` letter-spacing

- **Sync button** (4px 9px padding, border-radius 6px, 1px `HAIRLINE` border)
  - SVG refresh icon (11px) + "SYNC" label
  - DM Mono, `T_XS`, `MUTED_FG`
  - Hover: `PAPER_WARM` background, `FG` color

- **Bell button** (28px square, border-radius 7px, 1px `HAIRLINE` border)
  - Bell SVG icon, `MUTED_FG`
  - Notification dot: 6px circle, `GOLD` fill, positioned top-right with 1px `SURFACE` border
  - Hover: `PAPER_WARM` background, `FG` color

---

### 3.3 Hero Card

**Main dashboard card. The most important element.**

#### Container
- Border-radius: 14px
- Padding: 18px 22px 16px
- Border: 2px solid (color transitions between states, 0.5s)
- Background: three-layer composite:
  ```
  radial-gradient(ellipse 80% 60% at 88% 0%, HERO_TINT 0%, transparent 58%),
  radial-gradient(ellipse 70% 60% at 8% 100%, hsl(36 40% 90% / 0.75) 0%, transparent 60%),
  linear-gradient(155deg, HERO_BG1 0%, HERO_BG2 100%)
  ```
- Dot-grain pseudo-element overlay (3×3px, 5% opacity)

#### Interior layout (top to bottom):

1. **Header row** (space-between)
   - Left: label block
     - "FREE MONEY" + Arabic "ميزان" in `GOLD_LEAF` at 70% opacity
     - `GOLD` 20×1px underline rule below label
     - Sub-label: "after all upcoming charges"
   - Right: period block
     - Micro-label "PERIOD" in `MUTED`
     - Value: Playfair Display, `T_MD`, bold (e.g. "Jun 2026")

2. **Money display**
   - ₪ symbol: Playfair Display italic, 22px, `FG` at 38% opacity
   - Figure: Playfair Display 900 weight, **52px**, `FG`, `letter-spacing: -0.03em`
   - Lnum + tnum font features enabled
   - Animated with CountingLabel roll-up (600ms ease-out) on data change

3. **State badge** (inline-flex, 4px 10px padding, border-radius 3px, 0.5s transition)
   - `normal`: gold background tint (12%), `GOLD_LEAF` text — "ON TRACK"
   - `caution`: amber background tint (12%), `AMBER` text — "CAUTION"
   - `crisis`: red background tint (12%), `RED` text — "OVERSPENT"
   - SVG icon (10px) at left of text

4. **Legend row** (flex, gap 14px, flex-wrap)
   - Each item: 8px colored dot + label + Playfair value
   - Items: Spent (gold-leaf dot), Committed (red dot), Fuzzy (striped red dot), Budget (outline dot)
   - ₪ symbol italic before each value

5. **Timeline widget** (height 6px track, border-radius 999px)
   - Background track: `TRACK` color
   - Spent segment: `GOLD_LEAF`, left-aligned, animates on load (1.1s cubic-bezier)
   - Committed segment: `RED`, positioned after spent
   - Fuzzy segment: diagonal stripe pattern (red 55% opacity, 45deg)
   - Today marker: 2px `FG` vertical line, 18px tall, "TODAY" label above
   - Charge tick marks: 1.5px vertical marks at charge due dates
   - Month labels below: "1 Jun" (left) / "30 Jun" (right)

6. **"What changed today" row** (margin-top auto, border-top hairline)
   - Micro-label "TODAY'S CHANGES"
   - Inline items: income added, spend logged, charges changed
   - Separator: `·` in muted

---

### 3.4 Stat Column

**Fixed 290px right of hero card. 4 stacked cards.**

All cards: border-radius 14px, `SURFACE` background, `inset 0 0 0 1px HAIRLINE`

#### Card 1 — Total Spent
- Micro-label "TOTAL SPENT THIS MONTH"
- Context sub-label (e.g. "of ₪2,400 budget")
- Value: Playfair Display 700, 28px, `GOLD_LEAF`

#### Card 2 — Committed
- Micro-label "COMMITTED CHARGES"
- Context: "due this month"
- Value: Playfair Display 700, 26px, `RED`
- Delta indicator: ▲/▼ with `GREEN` (down) or `RED` (up)

#### Card 3 — Monthly Income
- Micro-label "INCOME THIS MONTH"
- Value: Playfair Display 700, 26px, `GREEN`
- Sub: number of income entries

#### Card 4 — Daily Allowance (flex:1, fills remaining height)
- Micro-label "DAILY ALLOWANCE"
- Period label right-aligned
- Value: Playfair Display 700, 28px, `GREEN`
- Explanation: `T_SM`, `MUTED`, `line-height 1.4`
- **Burn rate bars** (auto bottom of card):
  - 7-day mini bar chart (height 24px)
  - Past bars: `GREEN` fill
  - Future bars: `HAIRLINE` at 50% opacity
  - Day labels below: `T_MINI`, `MUTED`

---

### 3.5 Alert Banner

**Shown above hero row when fuzzy charges are pending.**

- Border-radius: 10px
- Background: `AMBER_BG`
- Border: 1px inset `AMBER_BD`
- Layout: horizontal flex, 9px 16px padding, gap 12px
- Left: badge "HEADS UP" — `T_MINI`, `AMBER` text, `hsl(38 50% 86%)` background, 4px border-radius
- Center: body text — `T_SM`, `FG`, with bold emphasis
- Right: amount — Playfair Display, 14px, `RED` bold

---

### 3.6 Category Panel

**First of three bottom panels.**

Header:
- Title: "SPENDING" + 4px gold square dot
- Meta: "this month" in `MUTED`
- Action button: "+ Income" in `GOLD_LEAF`, DM Mono, hover underline

Category rows (margin-bottom 11px, clickable with hover background):
- Colored 7px dot (category color)
- Category name: `T_BASE`, `FG`
- Percentage: `T_SM`, `MUTED`
- Amount right: Playfair Display, `T_MD`, bold
- Progress bar: 5px height, `TRACK` background, colored fill

Panel footer (border-top hairline, space-between):
- Left: "Total" label
- Right: total amount in Playfair Display

---

### 3.7 Upcoming Charges Panel

**Second bottom panel.**

Header:
- Title: "UPCOMING" + gold dot
- Meta: "this month"
- Action button: "+ Charge"

Charge rows (padding 9px 0, bottom hairline divider):
- Left: 4px colored stripe (urgency: `RED` urgent, `GOLD` soon, `MUTED` later)
- Name + recurring indicator (`↻` in `MUTED`, `T_XS`)
- Date below name: `T_SM`, `MUTED`
- Right: amount in Playfair Display
  - Due soon: `RED` color
  - Later: `MUTED_FG` color
  - Fuzzy: `AMBER` italic
- Timing: `T_SM`, `MUTED` (e.g. "in 3 days")
- ✓ button to mark paid (appears on hover or always visible)

Panel footer: total upcoming in `RED` Playfair Display

---

### 3.8 Recent Transactions Panel

**Third bottom panel.**

Header:
- Title: "RECENT" + gold dot
- Meta: "last 7 days"
- Action button: "+ Spend"

Transaction rows (padding 8px 0, bottom hairline divider):
- Icon tile: 30px × 30px, border-radius 8px, 1px `HAIRLINE_S` border, category SVG icon
- Name: `T_SM`, `FG`, truncated with ellipsis
- Meta: category label + date, `T_SM`, `MUTED`
- Amount right: Playfair Display, `T_MD`, bold
  - Spend: `FG` color
  - Income: `GREEN` color
- Time: `T_MINI`, `MUTED`

---

### 3.9 Page Footer

Three-column grid (1fr auto 1fr), top hairline border.

- Left: app name + version, `T_MINI`, `MUTED`, uppercase
- Center: "MIZĀN · STUDENT BUDGET", `T_MINI`, `MUTED`, letter-spaced
- Right: last sync time, `T_MINI`, `MUTED`, right-aligned

---

### 3.10 Toast Notification

**Temporary feedback, bottom-right corner.**

- Position: fixed, bottom 24px, right 24px, Z_TOAST
- Border-radius: 10px
- `SURFACE` background, 1px `HAIRLINE` border
- `0 8px 24px rgba(24,26,44,0.10)` drop-shadow
- Icon (12px) + message text (`T_SM`, `FG`) in flex row
- Auto-dismiss: 3000ms
- Slide-in from right: 200ms ease-out
- Variants: neutral (default), success (`GREEN` icon), error (`RED` icon)

---

### 3.11 Onboarding Dialog (first run only)

- Centered modal, `SURFACE` background, 14px border-radius
- Max-width: 420px
- `0 16px 48px rgba(24,26,44,0.14)` shadow
- Scrim overlay: `rgba(24,26,44,0.35)` behind
- Fields: Opening balance (₪), session name (optional)
- Primary CTA button: `NAVY` background, `GOLD` text, DM Mono
- Dismiss: closes app

---

### 3.12 Add Dialogs (Income / Spend / Charge)

Shared structure:
- Same container style as onboarding dialog
- Title in Playfair Display, `T_XL`
- Form fields: labeled inputs with `HAIRLINE` border, `SURFACE` background
- Focus ring: 2px `FOCUS` color
- Primary button: `NAVY` + `GOLD`
- Cancel: text button, `MUTED_FG`
- Error state: red border + `RED` message below field

---

## 4. Page Layouts

### 4.1 Dashboard

```
TOPBAR [breadcrumb · sparkline · period selector · status pill · sync · bell]
─────────────────────────────────────────────────────────────────────────
[ALERT BANNER — shown only when fuzzy charges pending]
[HERO CARD — free money, timeline, legend    ] [STAT COLUMN — 4 cards]
[CATEGORY PANEL  ] [UPCOMING PANEL  ] [RECENT TRANSACTIONS PANEL]
[PAGE FOOTER]
```

### 4.2 Activity

```
TOPBAR [ACTIVITY / 01]
─────────────────────────────────────────────────────────────────────────
[Date-grouped transaction ledger, full-width scrollable list]
[+ Income button] [+ Spend button] [+ Charge button] (action row top-right)
```

Ledger row structure:
- Date group header: "JUN 10" in DM Mono micro-label, hairline rule
- Each row: icon tile + name + category + amount + time

### 4.3 Insights

```
TOPBAR [INSIGHTS / 01]
─────────────────────────────────────────────────────────────────────────
[Spend-by-category breakdown — horizontal bar chart]
[Monthly trend — Playfair Display numbers, simple bar chart]
[Pattern insight — one sentence, only shown after 14 days + 20 transactions]
```

### 4.4 Settings

```
TOPBAR [SETTINGS / 01]
─────────────────────────────────────────────────────────────────────────
[Session info — opening balance, start date]
[Caution threshold — editable number field]
[Category reminder lead times — per-category]
[App version + data file location]
```

---

## 5. States & Interactions

### 5.1 Hero Card States

| State | Trigger | Border | Badge | Body |
|---|---|---|---|---|
| `normal` | Free money > threshold | `GOLD` | "ON TRACK" gold tint | Default |
| `caution` | Free money ≤ threshold | `AMBER` | "CAUTION" amber tint | Default |
| `crisis` | Free money ≤ 0 | `RED` | "OVERSPENT" red tint | Full category breakdown auto-shown |

State transition: `border-color 0.5s, background 0.5s`

### 5.2 Navigation Active State

Left border: transparent → `GOLD` (instant on click)
Background: transparent → `hsl(36 20% 94%)`
Text: `MUTED_FG` → `FG`

### 5.3 Page Transition

Incoming page: fade-in opacity 0→1, 150ms OutCubic easing. No translate. The opacity effect is removed after completion so it doesn't degrade text rendering.

### 5.4 Money Animation (CountingLabel)

On data refresh: number counts from old value to new over 600ms ease-out.
Only fires when the value actually changes.
Respects `prefers-reduced-motion` (skip animation, snap to final value).

### 5.5 Interactive Elements

All interactive elements:
- `cursor: pointer`
- Visible focus ring: 2px `FOCUS` color, 2px offset
- Hover transition: 120–200ms
- Minimum touch target: 33px height (nav items), 28px (icon buttons)

---

## 6. Animation System

| Element | Duration | Easing | Property |
|---|---|---|---|
| Page enter | 150ms | OutCubic | opacity |
| Hero card state | 500ms | ease | border-color, background |
| Timeline segments | 1100ms | cubic-bezier(.4,0,.2,1) | width |
| Money roll-up | 600ms | ease-out | displayed value |
| Status pill pulse | 2400ms | ease-out | box-shadow (infinite) |
| Panels on load | 280ms | ease-out | opacity + translateY(6px) |
| Nav item hover | 120ms | linear | background, color |
| Toast slide-in | 200ms | ease-out | translateX |
| Topbar sync spin | 600ms | linear | rotate (while syncing) |

**Reduced motion:** all animations collapse to instant (0ms, final value only).

---

## 7. Fonts Loading

```python
# Required font families (load before first paint):
# 1. Playfair Display — weights 700, 900
# 2. DM Mono — weights 400, 500
# 3. Noto Naskh Arabic — weights 400, 700
```

Fonts must be bundled or loaded from Google Fonts before the window shows. Missing fonts cause visual regression — fallback to `serif` / `monospace` respectively.

---

## 8. The One Structural Rule

> **All style values live in `tokens.py`. All style rules live in `stylesheet.py`. Widgets contain zero inline `setStyleSheet()` calls.**

This is the single rule that determines whether the app stays maintainable or breaks on every patch.

- `tokens.py` — color, spacing, radius, font-size constants only
- `stylesheet.py` — QSS rules assembled from tokens, applied once at startup
- Widgets — no `.setStyleSheet()`, no inline style strings, no `QPalette` overrides
- Exception: dynamic state changes (e.g. hero card border color on state change) use `setProperty` + CSS `[state="crisis"]` selector patterns, never string interpolation in widget code

---

## 9. What to Keep from Current Implementation

These are good patterns already in the codebase — keep them in the rebuild:

| Pattern | Location | Why keep |
|---|---|---|
| `CountingLabel` | `widgets/counting_label.py` | Animated number roll-up, well-isolated |
| `TimelineWidget` | `widgets/timeline_widget.py` | Custom-painted timeline, correct behavior |
| Controller → View signal pattern | `controllers/` | Clean MVC separation |
| `register_page_enter` callbacks | `main_window.py` | Page refresh on nav, correct approach |
| `PageIndex` enum | `constants.py` | Type-safe page indices |
| Onboarding dialog flow | `dialogs/onboarding_dialog.py` | First-run UX is correct |
| Service composition | `composition.py` | Backend wiring, unrelated to GUI |

---

## 10. What to Add (HTML mockup features missing from PyQt6)

| Feature | Description | Priority |
|---|---|---|
| Streak box in sidebar | 7-day gold segment activity streak | Medium |
| User avatar + online dot | Bottom of sidebar, navy circle with green status dot | Medium |
| Status pill with pulse | Animated pulse dot in topbar (replaces plain text) | High |
| Bell notification button | Topbar, with gold dot when pending items exist | Medium |
| Topbar sparkline value | "This month: ₪X" inline in topbar breadcrumb area | Low |
| Tooltip system | `data-tip` hover tooltips on numbers and labels | Low |
| Fade-up panel animation | Bottom panels animate in on page load | Low |
| "What changed today" row | Bottom of hero card, inline income/spend summary | Medium |

---

## 11. What to Remove

| Element | Reason |
|---|---|
| Scattered inline `setStyleSheet()` calls | Cause cascade conflicts, root of breakage |
| `DARK_MODE` flag in `tokens.py` | Dark mode deferred — remove the branch complexity |
| `stylesheet_manager.py` dual-theme switching | Premature — one theme only for now |
| `theme_manager.py` runtime switching | Same — remove complexity, add back later |
| `paper_widget.py` (if it exists only for inline QSS) | Consolidate into stylesheet.py |

---

## 12. Component Checklist (Pre-Delivery)

Before any page is considered done:

- [ ] Playfair Display renders on all monetary values
- [ ] DM Mono renders on all labels, nav items, buttons
- [ ] Gold accent visible on active nav item (left border + dot)
- [ ] Hero card shows correct state color (border + badge)
- [ ] Timeline segments animate on first load
- [ ] All buttons have hover state (120ms transition)
- [ ] All interactive elements have focus ring (`FOCUS` color)
- [ ] No emoji used as icon (SVG only)
- [ ] Money values use Playfair Display `font-feature-settings: 'lnum' 1, 'tnum' 1`
- [ ] ₪ symbol is italic and at ≤45% opacity
- [ ] MUTED_FG (`#475569`) passes 4.5:1 contrast on white
- [ ] Reduced-motion respected (no animations)
- [ ] Dialog closes on Escape key
- [ ] Tab order matches visual order on all forms

---

*This document is the contract. No implementation decision overrides it without updating this file first.*
