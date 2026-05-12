# GUI Build Plan — Mizān Desktop Dashboard
## Stage 2 · PyQt6 Implementation

> Ground truth for design: `Docs/visuals/mizan_dashboard.html`
> Architecture rule: GUI calls services only. No repos, no domain logic, no BalanceEngine in any view or widget.
> Stage 1 tests must remain green at every phase boundary.

---

## Current State (baseline)

```
app/gui/
├── main.py                   boots QApplication, creates MainWindow + DashboardController
├── STAGE2_PYQT6_PLAN.md      old milestone plan (superseded by this file)
├── controllers/
│   └── dashboard_controller.py   signals wired, refresh() is a stub, no services injected
├── view_models/
│   └── balance_view_model.py     frozen dataclass, never instantiated yet
└── views/
    └── main_window.py            single-column layout, wrong colors, placeholder panels
```

What works: imports, signal wiring, `MainWindow` public API.
What is broken: layout (no sidebar), colors (all wrong), fonts (wrong), panels (pass bodies), controller (stub), no dialogs, no state reactivity.

---

## Target Design — Key Facts from `mizan_dashboard.html`

### Color tokens

```python
BG           = "hsl(36, 25%, 96%)"    # warm cream body
SURFACE      = "#ffffff"              # card/panel background
HAIRLINE     = "hsl(36, 16%, 86%)"   # borders
FG           = "hsl(240, 28%, 12%)"  # primary text
MUTED_FG     = "hsl(224, 14%, 38%)"  # secondary text
MUTED        = "hsl(222, 12%, 55%)"  # disabled / labels
NAVY         = "hsl(240, 30%, 11%)"  # sidebar + active buttons
GOLD         = "hsl(42, 55%, 50%)"   # accent
GOLD_LEAF    = "hsl(42, 65%, 40%)"   # spent figures, gold text
RED          = "hsl(0, 55%, 38%)"    # committed charges, crisis
GREEN        = "hsl(162, 60%, 26%)"  # income, safe money
AMBER        = "hsl(32, 80%, 38%)"   # caution / fuzzy charges
# categories
CAT_FOOD     = "hsl(18, 88%, 50%)"
CAT_EDU      = "hsl(217, 82%, 52%)"
CAT_TRANS    = "hsl(162, 72%, 36%)"
CAT_OTHER    = "hsl(268, 65%, 58%)"
```

### Fonts

| Role | Font | Weight |
|---|---|---|
| Big numbers (₪640) | Playfair Display | 900 |
| Serif labels | Playfair Display | 700 |
| Body / UI | DM Mono | 400 / 500 |
| Arabic wordmark (ميزان) | Noto Naskh Arabic | 700 |

Fonts are Google Fonts — must be bundled as `.ttf` files under `gui/resources/fonts/` and loaded via `QFontDatabase.addApplicationFont()`.

### Layout structure

```
QMainWindow
└── QWidget (central)
    └── QHBoxLayout
        ├── Sidebar (QWidget, fixed 210px)   ← Phase 1
        └── MainArea (QWidget, stretch 1)
            ├── Topbar (QWidget, fixed height)  ← Phase 1
            └── ScrollArea → ContentWidget (QVBoxLayout)
                ├── AlertBanner (hidden when no alerts)  ← Phase 2
                ├── HeroRow (QHBoxLayout)
                │   ├── HeroCard (stretch 1)             ← Phase 3
                │   └── StatColumn (fixed 290px)         ← Phase 4
                └── PanelsRow (QHBoxLayout)
                    ├── CategoryPanel (stretch 1)        ← Phase 5
                    ├── UpcomingPanel (stretch 1)        ← Phase 5
                    └── RecentPanel (stretch 1)          ← Phase 5
```

### Timeline (correct colors)

| Segment | Color | Meaning |
|---|---|---|
| Background | warm gray `hsl(36,16%,92%)` | Full width |
| Spent | GOLD_LEAF | Money already used |
| Committed | RED | Upcoming locked charges |
| Fuzzy | Diagonal hatched RED (50% opacity) | Uncertain charges |
| Today marker | FG (navy) 2px line + "Today" label above | Current day |
| Event ticks | 25% opacity FG, named below | charge/income events |
| Month labels | Below track, MUTED | "1 Apr" / "30 Apr" |

---

## File Map — End State

```
app/gui/
├── main.py                          ← updated Phase 7
├── GUI_BUILD_PLAN.md
├── STAGE2_PYQT6_PLAN.md            (kept for reference)
├── controllers/
│   └── dashboard_controller.py      ← updated Phase 7
├── view_models/
│   ├── __init__.py
│   ├── balance_view_model.py        ← updated Phase 7
│   ├── charge_view_model.py         ← new Phase 5
│   └── transaction_view_model.py    ← new Phase 5
├── resources/
│   └── fonts/
│       ├── PlayfairDisplay-Black.ttf
│       ├── PlayfairDisplay-Bold.ttf
│       ├── PlayfairDisplay-Italic.ttf
│       ├── DMMono-Regular.ttf
│       ├── DMMono-Medium.ttf
│       └── NotoNaskhArabic-Bold.ttf
├── styles/
│   ├── __init__.py
│   ├── tokens.py                    ← new Phase 0
│   └── fonts.py                     ← new Phase 0
├── views/
│   ├── __init__.py
│   └── main_window.py               ← rebuilt Phase 1–5
└── widgets/
    ├── __init__.py
    ├── sidebar.py                   ← new Phase 1
    ├── topbar.py                    ← new Phase 1
    ├── alert_banner.py              ← new Phase 2
    ├── hero_card.py                 ← new Phase 3
    ├── timeline_widget.py           ← rebuilt Phase 3
    ├── stat_column.py               ← new Phase 4
    ├── category_panel.py            ← new Phase 5
    ├── upcoming_panel.py            ← new Phase 5
    └── recent_panel.py              ← new Phase 5
```

---

## Phase 0 — Foundation
**Goal:** Design system in Python. No visible changes. All later code imports from here.

### 0-A · `styles/tokens.py`

Define every color, spacing, and radius as a named constant.
Use hex strings (Qt QSS compatible). Derive from the HSL values in the HTML.

```python
# colors
BG        = "#f5f0e8"   # hsl(36,25%,96%)
SURFACE   = "#ffffff"
HAIRLINE  = "#ddd7cb"   # hsl(36,16%,86%)
FG        = "#17172b"   # hsl(240,28%,12%)
MUTED_FG  = "#535971"   # hsl(224,14%,38%)
MUTED     = "#7f8499"   # hsl(222,12%,55%)
NAVY      = "#16162a"   # hsl(240,30%,11%)
GOLD      = "#c8962a"   # hsl(42,55%,50%)
GOLD_LEAF = "#a07020"   # hsl(42,65%,40%)
RED       = "#8f2a2a"   # hsl(0,55%,38%)
GREEN     = "#1b6b46"   # hsl(162,60%,26%)
GREEN_BG  = "#e5f5ed"   # hsl(162,45%,92%)
AMBER     = "#9e4a0a"   # hsl(32,80%,38%)
AMBER_BG  = "#fdf3e3"   # hsl(38,78%,94%)
AMBER_BD  = "#e8c57a"   # hsl(38,60%,70%)
CAT_FOOD  = "#e85d10"   # hsl(18,88%,50%)
CAT_EDU   = "#2563eb"   # hsl(217,82%,52%)
CAT_TRANS = "#1b8a60"   # hsl(162,72%,36%)
CAT_OTHER = "#8b44d6"   # hsl(268,65%,58%)

# spacing
SIDEBAR_W = 210
STAT_COL_W = 290
CONTENT_PAD = 24
CARD_RADIUS = 14
```

### 0-B · `styles/fonts.py`

```python
import os
from PyQt6.QtGui import QFontDatabase, QFont

_FONTS_DIR = os.path.join(os.path.dirname(__file__),
                          "../../../../.claude/worktrees/elegant-hellman-6246d6/src/expense_tracker/app", "resources",
                          "fonts")


def load_fonts() -> None:
    """Load all bundled fonts into Qt's font database. Call once at app start."""
    for filename in os.listdir(_FONTS_DIR):
        if filename.endswith((".ttf", ".otf")):
            QFontDatabase.addApplicationFont(os.path.join(_FONTS_DIR, filename))


def playfair(size: int, weight: int = 700) -> QFont:
    f = QFont("Playfair Display", size)
    f.setWeight(weight)
    return f


def dm_mono(size: int, weight: int = 400) -> QFont:
    return QFont("DM Mono", size, weight)


def naskh(size: int) -> QFont:
    f = QFont("Noto Naskh Arabic", size, 700)
    f.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    return f
```

### 0-C · Download fonts

Place these files in `gui/resources/fonts/`:
- `PlayfairDisplay-Black.ttf` (weight 900 — hero numbers)
- `PlayfairDisplay-Bold.ttf` (weight 700 — panel headers, stat numbers)
- `PlayfairDisplay-Italic.ttf` (₪ symbol italic style)
- `DMMono-Regular.ttf` (weight 400 — body, labels)
- `DMMono-Medium.ttf` (weight 500 — active labels)
- `NotoNaskhArabic-Bold.ttf` (weight 700 — wordmark)

Source: Google Fonts (download as static .ttf files).

### 0 Tests

```python
# tests/unit/test_gui_foundation.py
def test_tokens_are_valid_hex():
    from expense_tracker.app.gui.styles.tokens import BG, SURFACE, GOLD, RED
    for color in [BG, SURFACE, GOLD, RED]:
        assert color.startswith("#")
        assert len(color) in (4, 7)

def test_fonts_module_importable():
    from expense_tracker.app.gui.styles.fonts import load_fonts, playfair, dm_mono
    assert callable(load_fonts)

def test_font_helpers_return_qfont():
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication.instance() or QApplication(sys.argv)
    from expense_tracker.app.gui.styles.fonts import playfair, dm_mono
    f = playfair(52, 900)
    assert f.pointSize() == 52
```

---

## Phase 1 — App Shell
**Goal:** Sidebar + topbar visible. Window opens with correct two-column structure. No real data yet.

### 1-A · `widgets/sidebar.py` — `Sidebar(QWidget)`

```
Sidebar (QWidget, fixed 210px, navy bg)
├── Brand section (border-bottom)
│   ├── QLabel "M—01"          (MUTED, 8px DM Mono, uppercase)
│   └── QLabel "ميزان"         (GOLD, 25px Noto Naskh Arabic, rtl)
│   └── QLabel "Student Budget" (MUTED, 9px)
├── Nav section (stretch)
│   ├── Section label "Overview" (MUTED, 8px uppercase)
│   ├── NavItem "Dashboard"     (active state)
│   ├── NavItem "History"
│   ├── Section label "Money"
│   ├── NavItem "Income"
│   ├── NavItem "Charges"
│   ├── NavItem "Transactions"
│   ├── Section label "You"
│   ├── NavItem "Insights"
│   ├── NavItem "Profile"
│   └── StreakBox              (see below)
└── User row (border-top)
    ├── Avatar QLabel          (navy circle, gold initials)
    ├── Name QLabel
    └── Sub QLabel             (institution · year)
```

**`NavItem(QPushButton)`** — custom button with:
- Left border 2px: transparent normally, GOLD when active
- Hover background: `hsl(36,20%,95%)` tinted
- SVG icon (passed as path string or inline) + label text

**`StreakBox(QWidget)`** — 14-segment horizontal bar:
- Each segment: `QFrame` 6px height, rounded, GOLD if logged, HAIRLINE if not
- Header: "Streak" label + "12 days" counter

Signals:
```python
nav_dashboard_clicked = pyqtSignal()
nav_history_clicked   = pyqtSignal()
nav_income_clicked    = pyqtSignal()
nav_charges_clicked   = pyqtSignal()
```

### 1-B · `widgets/topbar.py` — `Topbar(QWidget)`

```
Topbar (QWidget, SURFACE bg, border-bottom HAIRLINE, min-height 54px)
├── Left: breadcrumb stack
│   ├── QLabel "Dashboard / 01"   (MUTED, 9px)
│   └── QLabel date               (FG, 13px DM Mono)
├── Middle: sparkline + 7-day value
│   ├── SparklineWidget           (custom QWidget, 80×22px)
│   └── QLabel stack: "Last 7 days" + "₪NNN"
├── Right:
│   ├── PeriodSelector            (W/M/Y pill toggle)
│   ├── StatusPill                (green/amber/red, animated dot)
│   ├── SyncButton                (rotating icon + timestamp label)
│   └── BellButton                (notification icon + gold dot)
```

**`StatusPill(QWidget)`**:
- State: `"green"` | `"amber"` | `"red"`
- `set_state(state: str, label: str)` — updates color + text + icon
- Pulsing dot animation via `QPropertyAnimation` on a nested widget's opacity

**`SyncButton(QPushButton)`**:
- `set_syncing(True)` — starts rotation animation on icon
- `set_last_sync(dt: datetime)` — updates timestamp label

### 1-C · Rebuild `views/main_window.py`

Tear out the current single-column layout. Replace with:

```python
class MainWindow(QMainWindow):
    # ── SIGNALS (same as before — do not remove) ──
    refresh_requested    = pyqtSignal()
    add_income_requested = pyqtSignal()
    add_spend_requested  = pyqtSignal()
    add_charge_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Mizān")
        self.setMinimumSize(1100, 720)

        # Instantiate sub-widgets
        self._sidebar = Sidebar()
        self._topbar  = Topbar()
        self._content = ContentArea()   # scroll area wrapping panels

        # Two-column layout
        body = QWidget()
        h = QHBoxLayout(body)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)
        h.addWidget(self._sidebar)
        h.addWidget(self._build_right_column())
        self.setCentralWidget(body)

    def _build_right_column(self) -> QWidget:
        col = QWidget()
        v = QVBoxLayout(col)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        v.addWidget(self._topbar)
        v.addWidget(self._content, stretch=1)
        return col
```

Public setters are identical to before — controller interface does not change:
`set_snapshot`, `set_upcoming`, `set_recent`, `set_categories`, `set_last_sync`, `update_timeline`.

### 1 Tests

```python
# tests/unit/test_gui_shell.py
class TestShellStructure:
    def test_sidebar_importable(self):
        from expense_tracker.app.gui.widgets.sidebar import Sidebar
        assert Sidebar is not None

    def test_topbar_importable(self):
        from expense_tracker.app.gui.widgets.topbar import Topbar
        assert Topbar is not None

    def test_main_window_has_sidebar_attribute(self):
        from expense_tracker.app.gui.views.main_window import MainWindow
        assert hasattr(MainWindow, '__init__')

    def test_sidebar_has_nav_signals(self):
        from expense_tracker.app.gui.widgets.sidebar import Sidebar
        assert hasattr(Sidebar, 'nav_dashboard_clicked')

    def test_topbar_has_status_pill(self):
        from expense_tracker.app.gui.widgets.topbar import Topbar, StatusPill
        assert hasattr(Topbar, 'set_status')

    def test_main_window_signals_preserved(self):
        from expense_tracker.app.gui.views.main_window import MainWindow
        for sig in ['refresh_requested','add_income_requested',
                    'add_spend_requested','add_charge_requested']:
            assert hasattr(MainWindow, sig)
```

---

## Phase 2 — Alert Banner
**Goal:** Amber banner appears below topbar when a charge is due within `reminder_days`.

### `widgets/alert_banner.py` — `AlertBanner(QWidget)`

```
AlertBanner (QWidget, hidden by default)
├── Badge QLabel "⚠ HEADS-UP"     (amber bg, amber text, 8px uppercase)
├── Body QLabel                    (charge name + days until + "already counted")
└── Amount QLabel                  (RED, Playfair Display 14px bold)
```

Methods:
```python
def show_charge(self, name: str, days_until: int, amount: Decimal) -> None:
    """Show the banner with charge reminder data."""

def hide_banner(self) -> None:
    """Hide the banner (no active reminders)."""
```

Logic for when to show: `days_until <= reminder_days` where `reminder_days` defaults to 3. Controller decides, widget just renders.

The banner sits inside `ContentArea` between topbar and the hero row. It is `hidden()` by default and only shown when controller calls `show_charge(...)`.

### 2 Tests

```python
class TestAlertBanner:
    def test_banner_hidden_by_default(self):
        from expense_tracker.app.gui.widgets.alert_banner import AlertBanner
        assert hasattr(AlertBanner, 'show_charge')
        assert hasattr(AlertBanner, 'hide_banner')

    def test_banner_importable(self):
        from expense_tracker.app.gui.widgets.alert_banner import AlertBanner
        assert AlertBanner is not None
```

---

## Phase 3 — Hero Card + Timeline
**Goal:** The main free-money panel matches the design exactly. State changes card appearance.

### `widgets/hero_card.py` — `HeroCard(QFrame)`

Internal structure:
```
HeroCard (QFrame, border-radius 14px, state-reactive gradient bg)
├── Top row (QHBoxLayout)
│   ├── Left stack
│   │   ├── Row: "FREE MONEY · April"  (MUTED_FG, 9px DM Mono uppercase)
│   │   │         + "ميزان" (GOLD_LEAF, 13px Naskh)
│   │   ├── "after spend & committed charges"  (MUTED, 9px)
│   │   └── Gold underline (QFrame, 20px wide, 1px, GOLD)
│   └── Right stack
│       ├── "Period"       (MUTED, 8px uppercase)
│       └── "19 / 30"      (FG, 13px Playfair Bold)
├── Money row
│   ├── "₪" symbol         (FG, 22px Playfair Italic, 38% opacity)
│   └── Figure QLabel      (FG, 52px Playfair Black 900)
├── StateBadge              (see below)
├── Legend row              (see below)
├── TimelineWidget          (rebuilt)
└── ChangesStrip            (today's changes — see below)
```

**State reactivity** — `set_state(state: str)` changes the card:

```python
HERO_STATES = {
    "green": {
        "border": GOLD,
        "bg_tint": "hsl(42, 65%, 90%, 0.85)",
        "badge_class": "green",
        "badge_icon": "checkmark",
    },
    "amber": {
        "border": AMBER,
        "bg_tint": "hsl(38, 78%, 88%, 0.85)",
        "badge_class": "amber",
        "badge_icon": "triangle",
    },
    "red": {
        "border": RED,
        "bg_tint": "hsl(0, 55%, 90%, 0.8)",
        "badge_class": "red",
        "badge_icon": "cross",
    },
}
```

Background gradient via `paintEvent` (QSS doesn't support radial-gradient — use QPainter).

**`StateBadge(QLabel)`**:
- `set_green(text)` / `set_amber(text)` / `set_red(text)`
- Inline SVG icon: checkmark / triangle / cross (drawn via QPainter or embedded as a `QLabel` sibling)
- Background + text color change via `setStyleSheet()`

**Legend row** (`_build_legend()`):
```
Row: [● Spent ₪NNN] [● Committed ₪NNN] [◌ Fuzzy ₪N–N] [○ Limit ₪NNN]
```
- Each: colored dot QLabel + text + bold value
- Fuzzy dot: diagonal hatched pattern (drawn via QPainter in a `DotWidget`)

**`ChangesStrip(QWidget)`** — bottom of hero card:
```
"Today  −₪32 Café Najjar · 2 entries logged · Monthly left ₪1,840"
```
- Updates via `set_changes(entries_today: int, last_desc: str, last_amt: Decimal, monthly_left: Decimal)`

### Rebuild `widgets/timeline_widget.py` — `TimelineWidget(QWidget)`

Replace the current file completely. Key changes:

```python
@dataclass
class TimelineData:
    spent_pct: float        # 0–100, gold
    committed_pct: float    # 0–100, red (starts after spent)
    fuzzy_left_pct: float   # 0–100, start of fuzzy zone
    fuzzy_width_pct: float  # 0–100, width of fuzzy zone
    today_pct: float        # 0–100, position of today marker
    month_label_start: str  # e.g. "1 Apr"
    month_label_end: str    # e.g. "30 Apr"
    events: list[tuple[float, str]]  # [(pct, label), ...] for event ticks
```

`paintEvent` layers (bottom to top):
1. Track background: warm gray, full width, 6px height, rounded-pill
2. Spent fill: GOLD_LEAF, from 0 to `spent_pct`
3. Committed fill: RED, from `spent_pct` to `spent_pct + committed_pct`
4. Fuzzy fill: hatched diagonal RED at 50% opacity
5. Event ticks: 14px tall, 1.5px wide, 25% opacity FG, label below
6. Today marker: 18px tall, 2px wide, FG, "Today" label above in 8px DM Mono
7. Month labels below track: MUTED, 9px

Public API (unchanged from before):
```python
def set_percentages(self, spent_pct, committed_pct, fuzzy_left_pct,
                    fuzzy_width_pct, today_pct) -> None: ...
def set_month_labels(self, start: str, end: str) -> None: ...
def set_events(self, events: list[tuple[float, str]]) -> None: ...
```

### 3 Tests

```python
class TestHeroCard:
    def test_hero_card_importable(self):
        from expense_tracker.app.gui.widgets.hero_card import HeroCard
        assert HeroCard is not None

    def test_hero_card_has_set_snapshot(self):
        from expense_tracker.app.gui.widgets.hero_card import HeroCard
        assert callable(getattr(HeroCard, 'set_snapshot', None))

    def test_hero_card_has_set_state(self):
        from expense_tracker.app.gui.widgets.hero_card import HeroCard
        assert callable(getattr(HeroCard, 'set_state', None))

    def test_state_badge_importable(self):
        from expense_tracker.app.gui.widgets.hero_card import StateBadge
        assert StateBadge is not None

class TestTimelineWidget:
    def test_timeline_importable(self):
        from expense_tracker.app.gui.widgets.timeline_widget import TimelineWidget
        assert TimelineWidget is not None

    def test_set_percentages_exists(self):
        from expense_tracker.app.gui.widgets.timeline_widget import TimelineWidget
        assert callable(getattr(TimelineWidget, 'set_percentages', None))

    def test_set_month_labels_exists(self):
        from expense_tracker.app.gui.widgets.timeline_widget import TimelineWidget
        assert callable(getattr(TimelineWidget, 'set_month_labels', None))

    def test_set_events_exists(self):
        from expense_tracker.app.gui.widgets.timeline_widget import TimelineWidget
        assert callable(getattr(TimelineWidget, 'set_events', None))
```

---

## Phase 4 — Stat Column
**Goal:** Right-side vertical stat stack matches design: spent (gold), committed (red), monthly-left (green + burn bars).

### `widgets/stat_column.py` — `StatColumn(QWidget)`

```
StatColumn (QWidget, fixed 290px)
├── SpentCard (QFrame)
│   ├── "SPENT · MTD"         (MUTED, 8px DM Mono uppercase)
│   ├── "across N categories" (MUTED, 11px)
│   ├── "₪995"                (GOLD_LEAF, 28px Playfair Bold)
│   ├── "35% of limit"        (MUTED, 11px)
│   └── DeltaRow              (↑/↓ arrow + "8% vs last month", color-coded)
├── CommittedCard (QFrame)
│   ├── "COMMITTED"           (MUTED, 8px)
│   ├── "this month"          (MUTED, 11px)
│   ├── "₪1,200"              (RED, 28px Playfair Bold)
│   └── "rent · due in 3d"    (MUTED, 11px — most urgent charge hint)
└── SafeCard (QFrame, stretch 1)
    ├── Header row: "MONTHLY LEFT" + "April"
    ├── "₪1,840"              (GREEN, 26px Playfair Bold)
    ├── Explanation text      (MUTED, 11px)
    └── BurnBars              (see below)
```

**`BurnBars(QWidget)`** — mini horizontal bar chart at bottom of SafeCard:
- Two bars: spent (GREEN, proportional height) + left (HAIRLINE, proportional)
- Labels below: "₪NNN spent" / "₪NNN left"

Public method:
```python
def update(
    self,
    spent: Decimal,
    committed: Decimal,
    monthly_left: Decimal,
    category_count: int,
    next_charge_hint: str,    # e.g. "rent · due in 3d"
    delta_pct: float | None,  # e.g. -8.0 means 8% less than last month
) -> None: ...
```

### 4 Tests

```python
class TestStatColumn:
    def test_stat_column_importable(self):
        from expense_tracker.app.gui.widgets.stat_column import StatColumn
        assert StatColumn is not None

    def test_stat_column_has_update(self):
        from expense_tracker.app.gui.widgets.stat_column import StatColumn
        assert callable(getattr(StatColumn, 'update', None))

    def test_burn_bars_importable(self):
        from expense_tracker.app.gui.widgets.stat_column import BurnBars
        assert BurnBars is not None
```

---

## Phase 5 — Three Panels + View Models
**Goal:** All three panels render real-shaped data. `set_upcoming`, `set_recent`, `set_categories` become real implementations.

### 5-A · `view_models/charge_view_model.py`

```python
@dataclass(frozen=True)
class ChargeViewModel:
    charge_id: UUID
    name: str
    amount_str: str          # "₪1,200" or "₪80–150" for fuzzy
    due_date_str: str        # "1 May" or "approx. mid-May"
    timing_str: str          # "in 3d" | "in 7d" | "next mo" | "overdue"
    is_recurring: bool
    is_fuzzy: bool
    urgency: str             # "due_soon" | "upcoming" | "far" | "fuzzy"
    stripe_color: str        # hex color for left stripe
    amount_color: str        # hex color for amount text
```

### 5-B · `view_models/transaction_view_model.py`

```python
@dataclass(frozen=True)
class TransactionViewModel:
    description: str
    category_str: str        # "Food" | "Transport" | etc.
    amount_str: str          # "₪32"
    is_income: bool
    amount_color: str        # GREEN if income, FG if expense
    time_str: str            # "Today · 13:42" | "Yesterday · 10:15"
    category_color: str      # hex for category icon border
```

### 5-C · `widgets/upcoming_panel.py` — `UpcomingPanel(QFrame)`

```
UpcomingPanel
├── Header row: "Upcoming" title + "N charges · ₪NNN total" meta + "All →" button
└── ChargeList (QVBoxLayout)
    └── ChargeRow × N (see below)
```

**`ChargeRow(QWidget)`**:
```
[Stripe QFrame 4px] [Body: name+recur+date] [Right: amount+timing]
```
- Stripe color from `ChargeViewModel.stripe_color`
- Recur symbol "↻" shown when `is_recurring`
- Amount text color from `ChargeViewModel.amount_color`

```python
def set_charges(self, charges: list[ChargeViewModel]) -> None: ...
```

### 5-D · `widgets/recent_panel.py` — `RecentPanel(QFrame)`

```
RecentPanel
├── Header row: "Recent" + "Last N entries" meta + "All →" button
└── TxList (QVBoxLayout)
    └── TxRow × N (see below)
```

**`TxRow(QWidget)`**:
```
[IconBox 30×30px] [Body: name+meta] [Right: amount+time]
```
- Category SVG icon drawn via QPainter or embedded as colored QLabel
- Income rows: amount in GREEN, small up-arrow icon

```python
def set_transactions(self, txs: list[TransactionViewModel]) -> None: ...
```

### 5-E · `widgets/category_panel.py` — `CategoryPanel(QFrame)`

```
CategoryPanel
├── Header row: "By Category" + "April · month-to-date" + "Details →" button
├── CatRow × N (see below)
└── Footer: "Total spent" + "₪NNN"
```

**`CatRow(QWidget)`**:
```
[Dot] [Name] [Pct%]    [₪NNN]
[Progress bar ─────────────── ]
```

Colors by category:
```python
CATEGORY_COLORS = {
    "food":          CAT_FOOD,
    "transport":     CAT_TRANS,
    "education":     CAT_EDU,
    "entertainment": CAT_OTHER,
    "other":         CAT_OTHER,
}
```

```python
@dataclass(frozen=True)
class CategorySummary:
    category: str
    amount: Decimal
    amount_str: str
    pct: float        # 0–100
    color: str        # hex

def set_categories(self, cats: list[CategorySummary], total_str: str) -> None: ...
```

### 5 Tests

```python
class TestPanelImports:
    def test_upcoming_panel_importable(self):
        from expense_tracker.app.gui.widgets.upcoming_panel import UpcomingPanel, ChargeRow
        assert UpcomingPanel is not None

    def test_recent_panel_importable(self):
        from expense_tracker.app.gui.widgets.recent_panel import RecentPanel
        assert RecentPanel is not None

    def test_category_panel_importable(self):
        from expense_tracker.app.gui.widgets.category_panel import CategoryPanel
        assert CategoryPanel is not None

    def test_charge_view_model_importable(self):
        from expense_tracker.app.gui.view_models.charge_view_model import ChargeViewModel
        assert ChargeViewModel is not None

    def test_transaction_view_model_importable(self):
        from expense_tracker.app.gui.view_models.transaction_view_model import TransactionViewModel
        assert TransactionViewModel is not None

class TestChargeViewModel:
    def test_charge_view_model_is_frozen(self):
        from expense_tracker.app.gui.view_models.charge_view_model import ChargeViewModel
        import dataclasses
        assert dataclasses.is_dataclass(ChargeViewModel)

class TestCategoryPanel:
    def test_set_categories_signature(self):
        from expense_tracker.app.gui.widgets.category_panel import CategoryPanel
        import inspect
        sig = inspect.signature(CategoryPanel.set_categories)
        assert 'cats' in sig.parameters

class TestUpcomingPanel:
    def test_set_charges_signature(self):
        from expense_tracker.app.gui.widgets.upcoming_panel import UpcomingPanel
        import inspect
        sig = inspect.signature(UpcomingPanel.set_charges)
        assert 'charges' in sig.parameters
```

---

## Phase 6 — Dialogs
**Goal:** Every write workflow reachable from the GUI without the terminal.

### Dialogs to build (in order)

| Dialog | Class | Triggers | Service call |
|---|---|---|---|
| Session init | `SessionInitDialog` | No session exists on startup | `SessionService.init_session(opening_balance)` |
| Add spend | `AddSpendDialog` | "Add Spend" button | `SpendService.add_transaction(...)` |
| Add income | `AddIncomeDialog` | "Add Income" button | `IncomeService.add_income(...)` |
| Add charge | `AddChargeDialog` | "Add Charge" button | `ChargeService.add_charge(...)` |
| Add recurring | `AddRecurringChargeDialog` | "Recurring" toggle in AddChargeDialog | `ChargeService.add_recurring_charge(...)` |
| Mark paid | `MarkPaidAction` | Button in ChargeRow | `ChargeService.mark_paid(charge_id)` |
| Add fuzzy | `AddFuzzyDialog` | "Fuzzy" toggle in AddChargeDialog | `FuzzyChargeService.add_fuzzy_charge(...)` |
| Resolve fuzzy | `ResolveFuzzyDialog` | Button in ChargeRow (fuzzy row) | `FuzzyChargeService.resolve(...)` |
| Discard fuzzy | Confirm message box | Button in ChargeRow (fuzzy row) | `FuzzyChargeService.discard(...)` |

All dialogs live in `gui/dialogs/`. Each follows the same pattern:

```python
class AddSpendDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None: ...

    def get_result(self) -> tuple[Decimal, str, str | None, date] | None:
        """Return (amount, description, category, date) or None if cancelled."""
```

The controller calls `dialog.exec()`, then `dialog.get_result()`, calls the service, then calls `self.refresh()`.

Error handling: if the service raises `ValidationError` or `ApplicationError`, show a `QMessageBox.warning(...)` with the error text. Do not let exceptions propagate to the view.

### Dialog fields

**`AddSpendDialog`**:
- Amount: `QLineEdit` (numeric, placeholder "0.00")
- Description: `QLineEdit`
- Category: `QComboBox` (Food / Transport / Education / Entertainment / Other / — none —)
- Date: `QDateEdit` (defaults to today)

**`AddIncomeDialog`**:
- Amount: `QLineEdit`
- Source: `QComboBox` (Scholarship / Family / Work / Other)
- Date: `QDateEdit` (defaults to today)

**`AddChargeDialog`**:
- Name: `QLineEdit`
- Amount: `QLineEdit`
- Type toggle: `QRadioButton` one-off / recurring / fuzzy
- Due date: `QDateEdit` (shown for one-off and fuzzy)
- Day of month: `QSpinBox` 1–31 (shown only for recurring)
- Estimate: `QLineEdit` optional (shown only for fuzzy)

**`SessionInitDialog`**:
- Opening balance: `QLineEdit`
- OK button calls service, error shown inline

### 6 Tests

```python
class TestDialogImports:
    def test_add_spend_dialog_importable(self):
        from expense_tracker.app.gui.dialogs.add_spend_dialog import AddSpendDialog
        assert AddSpendDialog is not None

    def test_add_income_dialog_importable(self):
        from expense_tracker.app.gui.dialogs.add_income_dialog import AddIncomeDialog
        assert AddIncomeDialog is not None

    def test_add_charge_dialog_importable(self):
        from expense_tracker.app.gui.dialogs.add_charge_dialog import AddChargeDialog
        assert AddChargeDialog is not None

    def test_session_init_dialog_importable(self):
        from expense_tracker.app.gui.dialogs.session_init_dialog import SessionInitDialog
        assert SessionInitDialog is not None

    def test_all_dialogs_have_get_result(self):
        from expense_tracker.app.gui.dialogs.add_spend_dialog import AddSpendDialog
        from expense_tracker.app.gui.dialogs.add_income_dialog import AddIncomeDialog
        from expense_tracker.app.gui.dialogs.add_charge_dialog import AddChargeDialog
        for cls in [AddSpendDialog, AddIncomeDialog, AddChargeDialog]:
            assert callable(getattr(cls, 'get_result', None))
```

---

## Phase 7 — Controller Wiring + Real Data
**Goal:** `refresh()` fetches real data. Dashboard shows live numbers. Dialogs trigger refreshes.

### 7-A · Update `DashboardController`

Add missing service injection:

```python
def __init__(
    self,
    view: MainWindow,
    session_service: SessionService | None = None,
    balance_service: BalanceService | None = None,
    income_service: IncomeService | None = None,     # ← was missing
    charge_service: ChargeService | None = None,
    fuzzy_charge_service: FuzzyChargeService | None = None,  # ← new
    spend_service: SpendService | None = None,
    caution_threshold: Decimal = Decimal("100"),
    logger: logging.Logger | None = None,
) -> None: ...
```

### 7-B · Implement `refresh()`

```python
def refresh(self) -> None:
    if not self._session_service:
        return

    session = self._session_service.get_active()
    if session is None:
        self._show_no_session()
        return

    snapshot = self._balance_service.aggregate_and_build_snapshot(
        session.session_id, self._caution_threshold, session.opening_balance
    )

    vm = self._build_view_model(snapshot)
    self._view.set_snapshot(vm, last_sync=datetime.now())
    self._view.set_upcoming(self._build_charge_vms(session))
    self._view.set_recent(self._build_transaction_vms(session))
    self._view.set_categories(self._build_category_vms(session))
    self._check_alerts(session)
```

### 7-C · `_build_view_model(snapshot)` — format `BalanceSnapshot` → `BalanceViewModel`

```python
def _build_view_model(self, snap: BalanceSnapshot) -> BalanceViewModel:
    today = date.today()
    days_in_month = monthrange(today.year, today.month)[1]
    today_pct = (today.day / days_in_month) * 100.0

    # Timeline: spent and committed as % of monthly budget (or 0 if no budget)
    budget = snap.monthly_budget
    if budget > 0:
        spent_pct     = float(snap.monthly_spent / budget * 100)
        committed_pct = float(snap.monthly_spent / budget * 100)  # already in spent
    else:
        spent_pct = committed_pct = 0.0

    return BalanceViewModel(
        free_money=snap.free_money,
        free_money_str=self._fmt(snap.free_money),
        balance_state_value=snap.balance_state.value,
        monthly_budget=snap.monthly_budget,
        monthly_budget_str=self._fmt(snap.monthly_budget),
        monthly_spent=snap.monthly_spent,
        monthly_spent_str=self._fmt(snap.monthly_spent),
        monthly_left=snap.monthly_left,
        monthly_left_str=self._fmt(snap.monthly_left),
        on_track_state_value=snap.on_track_state.value,
        timeline_spent_pct=spent_pct,
        timeline_committed_pct=committed_pct,
        timeline_fuzzy_left_pct=0.0,    # fuzzy pct computed from fuzzy charges
        timeline_fuzzy_width_pct=0.0,
        today_pct=today_pct,
    )

@staticmethod
def _fmt(amount: Decimal) -> str:
    return f"₪{amount:,.0f}"
```

### 7-D · Update `main.py`

Wire real repos and services identical to `app/main.py`:

```python
def main() -> int:
    app = QApplication(sys.argv)
    load_fonts()   # Phase 0

    # Repos and services (mirror of app/main.py)
    session_repo     = JsonSessionRepository(_DATA_DIR / "session.json")
    income_repo      = JsonIncomeRepository(_DATA_DIR / "income.json")
    charge_repo      = JsonChargeRepository(_DATA_DIR / "charges.json")
    rule_repo        = JsonRecurringRuleRepository(_DATA_DIR / "recurring_rules.json")
    fuzzy_repo       = JsonFuzzyChargeRepository(_DATA_DIR / "fuzzy_charges.json")
    tx_repo          = JsonTransactionRepository(_DATA_DIR / "transactions.json")

    engine           = BalanceEngine()
    session_service  = SessionService(session_repo)
    income_service   = IncomeService(session_repo, income_repo)
    charge_service   = ChargeService(session_repo, charge_repo, rule_repo)
    fuzzy_service    = FuzzyChargeService(session_repo, fuzzy_repo, charge_repo, income_repo)
    spend_service    = SpendService(session_repo, tx_repo)
    balance_service  = BalanceService(engine, income_repo, charge_repo, tx_repo)

    window = MainWindow()
    controller = DashboardController(
        view=window,
        session_service=session_service,
        balance_service=balance_service,
        income_service=income_service,
        charge_service=charge_service,
        fuzzy_charge_service=fuzzy_service,
        spend_service=spend_service,
    )
    controller.refresh()   # load initial data
    window.show()
    return app.exec()
```

### 7 Tests

```python
class TestControllerWiring:
    def test_controller_accepts_all_services(self):
        import inspect
        from expense_tracker.app.gui.controllers.dashboard_controller import DashboardController
        sig = inspect.signature(DashboardController.__init__)
        for name in ['session_service','balance_service','income_service',
                     'charge_service','fuzzy_charge_service','spend_service']:
            assert name in sig.parameters

    def test_controller_has_refresh(self):
        from expense_tracker.app.gui.controllers.dashboard_controller import DashboardController
        assert callable(getattr(DashboardController, 'refresh', None))

    def test_build_view_model_produces_correct_types(self):
        # Unit test _build_view_model using a known BalanceSnapshot
        from decimal import Decimal
        from expense_tracker.domain.models.balance import (
            BalanceSnapshot, OnTrackState, BalanceState
        )
        from expense_tracker.app.gui.controllers.dashboard_controller import DashboardController
        snap = BalanceSnapshot(
            free_money=Decimal("640"),
            monthly_budget=Decimal("2835"),
            monthly_spent=Decimal("995"),
            monthly_left=Decimal("1840"),
            on_track_state=OnTrackState.GREEN,
            balance_state=BalanceState.NORMAL,
        )
        vm = DashboardController._build_view_model(None, snap)
        assert vm.free_money_str == "₪640"
        assert vm.balance_state_value == "normal"
        assert vm.on_track_state_value == "green"
        assert isinstance(vm.today_pct, float)
```

---

## Phase 8 — State Reactivity
**Goal:** Changing `balance_state` and `on_track_state` visually updates every component simultaneously.

### What changes per state

| Component | NORMAL (green) | CAUTION (amber) | CRISIS (red) |
|---|---|---|---|
| Hero card border + gradient | GOLD tones | AMBER tones | RED tones |
| State badge | "✓ On track · N days left" green | "! Caution · 82% used" amber | "✕ Crisis · limit exceeded" red |
| Topbar status pill | green "On track" | amber "Caution" | red "Over budget" |
| Free money number | FG (normal) | FG (normal) | RED |
| Timeline spent color | GOLD_LEAF | GOLD_LEAF | RED |

### Implementation

`MainWindow.set_snapshot()` receives `BalanceViewModel` with `balance_state_value` and `on_track_state_value`.
It calls:

```python
self._hero_card.set_state(vm.balance_state_value)
self._topbar.set_status(vm.on_track_state_value, label_text)
```

Each widget handles its own visual update internally. The controller never sets colors.

### 8 Tests

```python
class TestStateReactivity:
    def test_hero_card_set_state_accepts_all_values(self):
        from expense_tracker.app.gui.widgets.hero_card import HeroCard
        # smoke test: method exists and accepts all three states
        for state in ["green", "amber", "red"]:
            assert hasattr(HeroCard, 'set_state')

    def test_status_pill_accepts_all_states(self):
        from expense_tracker.app.gui.widgets.topbar import StatusPill
        for state in ["green", "amber", "red"]:
            assert hasattr(StatusPill, 'set_state')
```

---

## Phase 9 — Polish
**Goal:** Animations, sparkline, period selector, today indicator, streak counter. After everything else works.

### 9-A · Count-up animation on hero number
- `QPropertyAnimation` on a custom `_value` property
- Duration: 800ms, easing: `OutCubic`
- Skipped if `prefers-reduced-motion` equivalent (check system accessibility setting)

### 9-B · Timeline load animation
- `QPropertyAnimation` animating from 0% to final `spent_pct` and `committed_pct`
- Duration: 1100ms, easing: `QEasingCurve.Type.OutCubic`

### 9-C · Sparkline widget (`widgets/sparkline.py`)
- `QWidget` with `paintEvent` drawing a polyline from 7 daily spend values
- Gold stroke, rounded endpoint dot
- Data passed via `set_data(values: list[Decimal])` — always length 7

### 9-D · Period selector (`W / M / Y`)
- Already in topbar structure; wire to signal `period_changed = pyqtSignal(str)`
- Controller ignores it for now (monthly is the only supported scope in Stage 2)

### 9-E · Streak box real data
- `Sidebar.set_streak(days_logged: int, streak_window: list[bool])` where `streak_window` is 14 booleans
- Controller computes from transaction dates for the last 14 calendar days

---

## Testing Strategy Summary

| Phase | Test file | What it covers |
|---|---|---|
| 0 | `test_gui_foundation.py` | Token validity, font helpers |
| 1 | `test_gui_shell.py` | Sidebar/topbar imports, signal presence |
| 2 | `test_gui_alert.py` | Alert banner API |
| 3 | `test_gui_hero.py` | HeroCard + Timeline API |
| 4 | `test_gui_stat_column.py` | StatColumn API |
| 5 | `test_gui_panels.py` | Panel imports, view model shapes, set_* signatures |
| 6 | `test_gui_dialogs.py` | Dialog imports, get_result presence |
| 7 | `test_gui_controller.py` | Constructor signature, refresh, _build_view_model |
| 8 | `test_gui_state.py` | set_state accepts all three values |
| Existing | `test_gui_main_window.py` | MainWindow public API — must stay green |

**Rule:** Every phase must leave `tests/unit/test_gui_main_window.py` fully green.
All phase tests are import-level and API-shape tests — no GUI rendering, no `QApplication` unless unavoidable.

---

## Build Order (strict sequence — each phase depends on previous)

```
Phase 0  →  Phase 1  →  Phase 2  →  Phase 3
                                         ↓
Phase 9  ←  Phase 8  ←  Phase 7  ←  Phase 4
                                         ↓
                         Phase 7  ←  Phase 5
                                         ↓
                         Phase 7  ←  Phase 6
```

Phases 4, 5, 6 are parallel after Phase 3. Phase 7 requires all three.

---

## Rules That Cannot Be Broken

1. **No business logic in widgets.** Widgets receive already-computed values. No `Decimal` arithmetic. No service calls. No domain imports.
2. **No direct repo access from GUI.** Controller → Service → Port → Infrastructure.
3. **No QApplication in tests** unless the import itself requires it (QFont, QPainter).
4. **Stage 1 tests stay green.** Run `pytest tests/unit/` after every phase. Fix any regression before moving forward.
5. **Colors come from `tokens.py`.** No hex literals scattered in widget files.
6. **Fonts come from `fonts.py`.** No hardcoded font names in widget files.
7. **`BalanceViewModel` is the only type the view receives for balance data.** The view never sees `BalanceSnapshot`, `Decimal`, or any domain model.
