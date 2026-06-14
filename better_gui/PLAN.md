# Mizān GUI v2 — Implementation Plan (Phase 1–5)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fully working Dashboard page in `gui_v2/`, connected to real backend services, switchable from the existing `gui/` via a one-line flag.

**Architecture:** `gui_v2/` is a clean PyQt6 implementation that follows the structural rule: all design values in `tokens.py`, all QSS rules in `stylesheet.py`, all `QFont` construction in `fonts.py`, zero inline `setStyleSheet()` in any widget. The Dashboard controller reads from existing unchanged services and pushes formatted data into views via `set_*` methods.

**Tech Stack:** Python 3.10+, PyQt6 6.7+, existing backend services (unchanged)

**Spec refs:** `better_gui/DESIGN.md`, `better_gui/IMPLEMENTATION_SPEC.md`

---

## File Map

```
src/expense_tracker/app/
  gui/main.py                              MODIFY  — add USE_GUI_V2 flag at top
  gui_v2/__init__.py                       CREATE
  gui_v2/main.py                           CREATE  — entry point
  gui_v2/constants.py                      CREATE  — PageIndex enum
  gui_v2/tokens.py                         CREATE  — all design values
  gui_v2/fonts.py                          CREATE  — QFont builders
  gui_v2/stylesheet.py                     CREATE  — all QSS rules
  gui_v2/resources/fonts/                  CREATE  — symlink to gui/resources/fonts/
  gui_v2/view_models/__init__.py           CREATE
  gui_v2/view_models/balance_view_model.py CREATE  — copy + no changes needed
  gui_v2/view_models/ledger_view_model.py  CREATE  — copy + no changes needed
  gui_v2/views/__init__.py                 CREATE
  gui_v2/views/main_window.py              CREATE  — shell: sidebar + topbar + stacked pages
  gui_v2/views/dashboard_page.py           CREATE  — hero row + stat column + panels + footer
  gui_v2/widgets/__init__.py               CREATE
  gui_v2/widgets/sidebar.py               CREATE  — brand + nav + streak + user
  gui_v2/widgets/topbar.py                CREATE  — breadcrumb + pill + sync + bell
  gui_v2/widgets/hero_card.py             CREATE  — paintEvent gradient + state system
  gui_v2/widgets/timeline_widget.py       CREATE  — copy from gui/ + strip tokens import
  gui_v2/widgets/counting_label.py        CREATE  — copy from gui/ (no changes)
  gui_v2/widgets/alert_banner.py          CREATE  — amber warning strip
  gui_v2/widgets/stat_column.py           CREATE  — 4 stat cards
  gui_v2/widgets/panels.py               CREATE  — Category, Upcoming, Recent panels
  gui_v2/controllers/__init__.py          CREATE
  gui_v2/controllers/dashboard_controller.py CREATE — thin orchestrator
  gui_v2/dialogs/__init__.py              CREATE
  gui_v2/dialogs/onboarding_dialog.py    CREATE  — first-run dialog
  gui_v2/dialogs/add_income_dialog.py    CREATE
  gui_v2/dialogs/add_spend_dialog.py     CREATE
  gui_v2/dialogs/add_charge_dialog.py    CREATE
tests/unit/gui_v2/
  test_balance_view_model.py             CREATE  — ViewModel unit tests
```

---

## Task 1: Foundation — tokens, constants, fonts

**Files:**
- Create: `src/expense_tracker/app/gui_v2/__init__.py`
- Create: `src/expense_tracker/app/gui_v2/constants.py`
- Create: `src/expense_tracker/app/gui_v2/tokens.py`
- Create: `src/expense_tracker/app/gui_v2/fonts.py`

- [ ] **Step 1: Create the package and constants**

```python
# src/expense_tracker/app/gui_v2/__init__.py
# (empty)
```

```python
# src/expense_tracker/app/gui_v2/constants.py
from __future__ import annotations
from enum import IntEnum

class PageIndex(IntEnum):
    DASHBOARD = 0
    ACTIVITY  = 1
    INSIGHTS  = 2
    SETTINGS  = 3
```

- [ ] **Step 2: Create tokens.py**

```python
# src/expense_tracker/app/gui_v2/tokens.py
"""All design values. No logic, no imports. Change values here only."""
from __future__ import annotations

# ── BACKGROUND & SURFACE ─────────────────────────────────────────────────────
BG          = "#f7f3ec"   # warm cream body
PAPER_WARM  = "#f3ede0"   # deeper warm surface (streak box, accents)
SURFACE     = "#ffffff"   # cards, sidebar, topbar

# ── BORDERS ──────────────────────────────────────────────────────────────────
HAIRLINE    = "#e2dccd"   # standard border
HAIRLINE_S  = "#cdc4ae"   # stronger border

# ── TEXT ─────────────────────────────────────────────────────────────────────
FG          = "#181a2c"   # primary text (near-black navy)
MUTED_FG    = "#475569"   # secondary text (min 4.5:1 on white)
MUTED       = "#838897"   # disabled, micro-labels
DISABLED    = "#a8a8b8"

# ── BRAND ────────────────────────────────────────────────────────────────────
NAVY        = "#16172a"   # action buttons, avatar background
GOLD        = "#c79a39"   # primary accent, active nav border
GOLD_LEAF   = "#a87c24"   # spent figures, active text, links
FOCUS       = "#f1b619"   # focus rings

# ── SEMANTIC ─────────────────────────────────────────────────────────────────
RED         = "#962e2e"   # committed charges, crisis
GREEN       = "#1b6a4f"   # income, safe money
GREEN_BG    = "#dff1ea"
AMBER       = "#f59e0b"   # caution, fuzzy charges
AMBER_BG    = "#fbeed4"
AMBER_BD    = "#dcb476"

# ── CATEGORY COLORS ──────────────────────────────────────────────────────────
CAT_FOOD    = "#ee6815"
CAT_EDU     = "#256de7"
CAT_TRANS   = "#199f6e"
CAT_OTHER   = "#9456db"

CATEGORY_COLORS: dict[str, str] = {
    "food":          CAT_FOOD,
    "transport":     CAT_TRANS,
    "education":     CAT_EDU,
    "entertainment": CAT_OTHER,
    "other":         CAT_OTHER,
}

# ── TIMELINE ─────────────────────────────────────────────────────────────────
TRACK       = "#ece6da"   # background track

# ── HERO CARD ────────────────────────────────────────────────────────────────
HERO_BG1    = "#fbf7ea"   # gradient start
HERO_BG2    = "#efe9da"   # gradient end
# Hero tint RGBA kept in hero_card.py (not a hex string — avoids test issues)

# ── TYPE SCALE (px) ──────────────────────────────────────────────────────────
# T_MINI / T_XS / T_SM are all 11px but serve different semantic roles:
#   T_SM   = body text in panels
#   T_XS   = caption text, small labels
#   T_MINI = metadata: dates, timing, sub-labels
T_MICRO = 10
T_MINI  = 11   # metadata
T_XS    = 11   # captions
T_SM    = 11   # body text
T_BASE  = 12
T_MD    = 13
T_LG    = 15
T_XL    = 18

# ── LAYOUT ───────────────────────────────────────────────────────────────────
SIDEBAR_W    = 210
STAT_COL_W   = 290
TOPBAR_H     = 54
CONTENT_PAD  = 24
CARD_RADIUS  = 14

# ── SPACING ──────────────────────────────────────────────────────────────────
SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 16
SPACE_LG = 24
SPACE_XL = 32
```

- [ ] **Step 3: Create fonts.py**

```python
# src/expense_tracker/app/gui_v2/fonts.py
"""
Central QFont factory. All widgets call these functions instead of
constructing QFont inline. This is the only place font-feature-settings
(lnum/tnum) are applied — QSS does not support font-feature-settings.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from expense_tracker.app.gui_v2 import tokens


def money(size: int = 52, weight: int = 900) -> QFont:
    """Playfair Display with lnum + tnum for monetary values."""
    f = QFont("Playfair Display", size)
    f.setWeight(weight)
    try:
        f.setFeature(QFont.Tag.fromString("lnum"), 1)
        f.setFeature(QFont.Tag.fromString("tnum"), 1)
    except AttributeError:
        pass  # PyQt6 < 6.6 — feature tags unavailable, degrade gracefully
    return f


def money_sm(size: int = 28) -> QFont:
    """Smaller Playfair Display for stat cards."""
    return money(size=size, weight=700)


def label(size: int = tokens.T_SM) -> QFont:
    """DM Mono for labels, metadata, nav items, buttons."""
    return QFont("DM Mono", size)


def label_bold(size: int = tokens.T_SM) -> QFont:
    f = QFont("DM Mono", size)
    f.setWeight(600)
    return f


def arabic(size: int = 25) -> QFont:
    """Noto Naskh Arabic for the brand wordmark only."""
    f = QFont("Noto Naskh Arabic", size)
    f.setWeight(700)
    return f


def load_fonts(resource_dir: str | None = None) -> None:
    """Register bundled font files with Qt's font database."""
    from pathlib import Path
    from PyQt6.QtGui import QFontDatabase

    fonts_dir = Path(resource_dir) if resource_dir else (
        Path(__file__).parent / "resources" / "fonts"
    )
    if not fonts_dir.exists():
        # Fall back to gui/ fonts directory
        fonts_dir = Path(__file__).parent.parent / "gui" / "resources" / "fonts"

    for font_file in fonts_dir.glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(font_file))
    for font_file in fonts_dir.glob("*.otf"):
        QFontDatabase.addApplicationFont(str(font_file))
```

- [ ] **Step 4: Verify imports resolve**

```bash
cd /home/dark-vader/PycharmProjects/student-expense-tracker
python -c "from src.expense_tracker.app.gui_v2 import tokens, constants; print('OK')"
```

Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add src/expense_tracker/app/gui_v2/
git commit -m "feat(gui_v2): add foundation tokens, constants, fonts"
```

---

## Task 2: stylesheet.py + main.py skeleton + flag

**Files:**
- Create: `src/expense_tracker/app/gui_v2/stylesheet.py`
- Create: `src/expense_tracker/app/gui_v2/main.py`
- Modify: `src/expense_tracker/app/gui/main.py`

- [ ] **Step 1: Create stylesheet.py**

```python
# src/expense_tracker/app/gui_v2/stylesheet.py
"""
All QSS rules for gui_v2. Applied ONCE at startup via app.setStyleSheet().
No widget ever calls setStyleSheet() — all appearance lives here.

IMPORTANT PyQt6 constraints respected here:
  - No `transition:` (silently ignored by Qt)
  - No `@keyframes` or `animation:` (silently ignored)
  - No `box-shadow` (use border for inset, QGraphicsDropShadowEffect for drop)
  - No `cursor:` (use widget.setCursor() in __init__)
  - No `font-feature-settings` (use fonts.py QFont.setFeature())
  - :hover pseudostate works for INSTANT color/background changes only
"""
from __future__ import annotations

from expense_tracker.app.gui_v2 import tokens as t


def build() -> str:
    return f"""

/* ── APP ROOT ─────────────────────────────────────────────────────────── */
QWidget#appRoot {{
    background: {t.BG};
    font-family: "DM Mono", Consolas, monospace;
}}

/* ── SIDEBAR ──────────────────────────────────────────────────────────── */
QWidget#sidebar {{
    background: {t.SURFACE};
    border-right: 1px solid {t.HAIRLINE};
}}
QLabel#sbTag {{
    font-size: {t.T_MICRO}px;
    letter-spacing: 3px;
    color: {t.MUTED};
    background: transparent;
    text-transform: uppercase;
}}
QLabel#sbWordmark {{
    color: {t.GOLD_LEAF};
    background: transparent;
}}
QPushButton#navItem {{
    font-family: "DM Mono";
    font-size: {t.T_BASE}px;
    letter-spacing: 1px;
    color: {t.MUTED_FG};
    background: transparent;
    border: none;
    border-left: 2px solid transparent;
    text-align: left;
    padding: 0 12px 0 18px;
}}
QPushButton#navItem:hover {{
    background: rgba(236,230,218,0.7);
    color: {t.FG};
}}
QPushButton#navItem[active="true"] {{
    background: #ece8de;
    color: {t.FG};
    border-left: 2px solid {t.GOLD};
}}
QWidget#streakBox {{
    background: {t.PAPER_WARM};
    border-radius: 10px;
}}
QLabel#streakLabel {{
    font-size: {t.T_MICRO}px;
    letter-spacing: 3px;
    color: {t.MUTED};
    background: transparent;
}}

/* ── TOPBAR ───────────────────────────────────────────────────────────── */
QWidget#topbar {{
    background: {t.SURFACE};
    border-bottom: 1px solid {t.HAIRLINE};
}}
QLabel#tbBcLabel {{
    font-size: {t.T_MINI}px;
    letter-spacing: 2px;
    color: {t.MUTED};
    background: transparent;
}}
QLabel#tbDate {{
    font-size: {t.T_MD}px;
    font-weight: 500;
    color: {t.FG};
    background: transparent;
}}
QPushButton#tbSync {{
    font-family: "DM Mono";
    font-size: {t.T_XS}px;
    color: {t.MUTED_FG};
    background: transparent;
    border: 1px solid {t.HAIRLINE};
    border-radius: 6px;
    padding: 4px 9px;
}}
QPushButton#tbSync:hover {{
    background: {t.PAPER_WARM};
    color: {t.FG};
}}
QPushButton#tbBell {{
    background: transparent;
    border: 1px solid {t.HAIRLINE};
    border-radius: 7px;
}}
QPushButton#tbBell:hover {{
    background: {t.PAPER_WARM};
}}

/* ── STATUS PILL ──────────────────────────────────────────────────────── */
QWidget#statusPill[state="green"] {{
    background: {t.GREEN_BG};
    border: 1px solid #9ed4be;
    border-radius: 999px;
}}
QWidget#statusPill[state="amber"] {{
    background: {t.AMBER_BG};
    border: 1px solid {t.AMBER_BD};
    border-radius: 999px;
}}
QWidget#statusPill[state="red"] {{
    background: #f5dcdc;
    border: 1px solid #d48888;
    border-radius: 999px;
}}
QLabel#pillText[state="green"] {{ color: {t.GREEN}; background: transparent; }}
QLabel#pillText[state="amber"] {{ color: {t.AMBER}; background: transparent; }}
QLabel#pillText[state="red"]   {{ color: {t.RED};   background: transparent; }}

/* ── CARDS & PANELS ───────────────────────────────────────────────────── */
QFrame#card {{
    background: {t.SURFACE};
    border: 1px solid {t.HAIRLINE};
    border-radius: {t.CARD_RADIUS}px;
}}
QLabel#cardMicro {{
    font-size: {t.T_MICRO}px;
    letter-spacing: 2px;
    color: {t.MUTED};
    background: transparent;
}}
QLabel#cardTitle {{
    font-size: {t.T_SM}px;
    font-weight: 500;
    color: {t.FG};
    background: transparent;
}}
QLabel#cardMeta {{
    font-size: {t.T_SM}px;
    color: {t.MUTED};
    background: transparent;
}}
QLabel#emptyState {{
    font-size: {t.T_SM}px;
    color: {t.MUTED};
    background: transparent;
}}

/* ── HERO CARD — border-color only; gradient is in paintEvent ────────── */
QFrame#heroCard {{
    border-radius: {t.CARD_RADIUS}px;
    border: 2px solid {t.GOLD};
}}
QFrame#heroCard[balanceState="normal"]  {{ border-color: {t.GOLD}; }}
QFrame#heroCard[balanceState="caution"] {{ border-color: {t.AMBER}; }}
QFrame#heroCard[balanceState="crisis"]  {{ border-color: {t.RED}; }}

/* ── HERO CARD LABELS ────────────────────────────────────────────────── */
QLabel#heroMiniLabel {{
    font-size: {t.T_MINI}px;
    letter-spacing: 3px;
    color: {t.MUTED_FG};
    background: transparent;
}}
QLabel#heroSubLabel {{
    font-size: {t.T_MINI}px;
    color: {t.MUTED};
    background: transparent;
}}
QLabel#moneyValue {{
    font-size: 52px;
    font-weight: 900;
    color: {t.FG};
    background: transparent;
    font-family: "Playfair Display";
    letter-spacing: -1px;
}}
QLabel#moneySym {{
    font-size: 22px;
    font-family: "Playfair Display";
    color: {t.FG};
    background: transparent;
}}

/* ── STATE BADGE ─────────────────────────────────────────────────────── */
QLabel#stateBadge {{
    font-size: {t.T_MINI}px;
    letter-spacing: 2px;
    padding: 4px 10px;
    border-radius: 3px;
    background: transparent;
}}
QLabel#stateBadge[state="normal"]  {{ background: rgba(199,154,57,0.12);  color: {t.GOLD_LEAF}; }}
QLabel#stateBadge[state="caution"] {{ background: rgba(245,158,11,0.12);  color: {t.AMBER}; }}
QLabel#stateBadge[state="crisis"]  {{ background: rgba(150,46,46,0.12);   color: {t.RED}; }}

/* ── ALERT BANNER ────────────────────────────────────────────────────── */
QFrame#alertBanner {{
    background: {t.AMBER_BG};
    border: 1px solid {t.AMBER_BD};
    border-radius: 10px;
}}
QLabel#alertBadge {{
    font-size: {t.T_MINI}px;
    letter-spacing: 2px;
    background: rgba(220,180,118,0.4);
    color: {t.AMBER};
    border-radius: 4px;
    padding: 3px 8px;
}}
QLabel#alertBody {{
    font-size: {t.T_SM}px;
    color: {t.FG};
    background: transparent;
}}
QLabel#alertAmt {{
    font-family: "Playfair Display";
    font-size: 14px;
    font-weight: 700;
    color: {t.RED};
    background: transparent;
}}

/* ── ACTION BUTTONS ──────────────────────────────────────────────────── */
QPushButton#actionBtn {{
    font-family: "DM Mono";
    font-size: {t.T_SM}px;
    font-weight: 500;
    background: {t.NAVY};
    color: {t.GOLD};
    border: none;
    border-radius: 6px;
    padding: 9px 16px;
    letter-spacing: 1px;
}}
QPushButton#actionBtn:hover {{
    background: {t.FG};
}}
QPushButton#linkBtn {{
    font-family: "DM Mono";
    font-size: {t.T_SM}px;
    color: {t.GOLD_LEAF};
    background: transparent;
    border: none;
    padding: 2px 4px;
}}
QPushButton#linkBtn:hover {{
    color: {t.FG};
}}

/* ── SCROLL AREAS ─────────────────────────────────────────────────────── */
QScrollArea {{ background: {t.BG}; border: none; }}
QScrollBar:vertical {{
    background: transparent; width: 6px; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {t.HAIRLINE_S}; border-radius: 3px; min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* ── DIALOGS ─────────────────────────────────────────────────────────── */
QDialog {{
    background: {t.SURFACE};
    border-radius: {t.CARD_RADIUS}px;
}}
QLabel#dialogTitle {{
    font-family: "Playfair Display";
    font-size: {t.T_XL}px;
    font-weight: 700;
    color: {t.FG};
    background: transparent;
}}
QLineEdit, QComboBox, QDateEdit {{
    font-family: "DM Mono";
    font-size: {t.T_SM}px;
    color: {t.FG};
    background: {t.SURFACE};
    border: 1px solid {t.HAIRLINE};
    border-radius: 6px;
    padding: 8px 10px;
}}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
    border-color: {t.FOCUS};
    outline: none;
}}
QLabel#fieldLabel {{
    font-size: {t.T_SM}px;
    color: {t.MUTED_FG};
    background: transparent;
}}
QLabel#fieldError {{
    font-size: {t.T_XS}px;
    color: {t.RED};
    background: transparent;
}}

/* ── FOOTER ───────────────────────────────────────────────────────────── */
QLabel#footerText {{
    font-size: {t.T_MINI}px;
    letter-spacing: 2px;
    color: rgba(131,136,151,0.7);
    background: transparent;
}}
"""
```

- [ ] **Step 2: Create gui_v2/main.py skeleton**

```python
# src/expense_tracker/app/gui_v2/main.py
from __future__ import annotations

import logging
import sys
from decimal import Decimal
from pathlib import Path

from PyQt6.QtWidgets import QApplication

_HERE = Path(__file__).resolve()
_SRC_DIR = _HERE.parents[3]
_PROJECT_ROOT = _SRC_DIR.parent
_DATA_DIR = _PROJECT_ROOT / "data"

if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


def main() -> int:
    logger = logging.getLogger(__name__)
    app = QApplication.instance() or QApplication(sys.argv)

    from expense_tracker.app.gui_v2.fonts import load_fonts
    from expense_tracker.app.gui_v2.stylesheet import build as build_stylesheet

    load_fonts()
    app.setStyleSheet(build_stylesheet())

    from expense_tracker.app.composition import build_services
    try:
        services = build_services(_DATA_DIR, logger=logger)
    except Exception:
        logger.exception("Failed to initialise services")
        return 1

    # First-run onboarding
    if services.session_service.get_active() is None:
        from expense_tracker.app.gui_v2.dialogs.onboarding_dialog import OnboardingDialog
        dlg = OnboardingDialog()
        if not dlg.exec():
            return 0
        try:
            services.session_service.init_session(dlg.opening_balance)
        except Exception:
            logger.exception("Failed to create session")
            return 1

    from expense_tracker.app.gui_v2.views.main_window import MainWindow
    window = MainWindow()
    window._wire_controllers(services)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: Add USE_GUI_V2 flag to gui/main.py**

Open `src/expense_tracker/app/gui/main.py` and add these lines at the very top, before any existing imports:

```python
# ── GUI VERSION SWITCH ─────────────────────────────────────────────────────
# Set USE_GUI_V2 = True to run the rebuilt gui_v2 interface.
# Set to False to run the original gui (for regression comparison).
USE_GUI_V2 = True

if USE_GUI_V2:
    from expense_tracker.app.gui_v2.main import main
    if __name__ == "__main__":
        raise SystemExit(main())
else:
    pass  # existing gui/main.py code runs below unchanged
# ──────────────────────────────────────────────────────────────────────────
```

- [ ] **Step 4: Commit**

```bash
git add src/expense_tracker/app/gui_v2/stylesheet.py \
        src/expense_tracker/app/gui_v2/main.py \
        src/expense_tracker/app/gui/main.py
git commit -m "feat(gui_v2): add stylesheet, main entry point, and version flag"
```

---

## Task 3: MainWindow shell (placeholder pages)

**Files:**
- Create: `src/expense_tracker/app/gui_v2/views/__init__.py`
- Create: `src/expense_tracker/app/gui_v2/views/main_window.py`
- Create: `src/expense_tracker/app/gui_v2/views/dashboard_page.py` (placeholder)
- Create: `src/expense_tracker/app/gui_v2/views/activity_page.py` (placeholder)
- Create: `src/expense_tracker/app/gui_v2/views/insights_page.py` (placeholder)
- Create: `src/expense_tracker/app/gui_v2/views/settings_page.py` (placeholder)

- [ ] **Step 1: Create placeholder pages**

```python
# src/expense_tracker/app/gui_v2/views/__init__.py
# (empty)
```

```python
# src/expense_tracker/app/gui_v2/views/activity_page.py
from __future__ import annotations
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

class ActivityPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("activityPage")
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Activity — coming soon"))
```

```python
# src/expense_tracker/app/gui_v2/views/insights_page.py
from __future__ import annotations
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

class InsightsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("insightsPage")
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Insights — coming soon"))
```

```python
# src/expense_tracker/app/gui_v2/views/settings_page.py
from __future__ import annotations
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

class SettingsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("settingsPage")
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Settings — coming soon"))
```

- [ ] **Step 2: Create MainWindow with placeholder sidebar/topbar**

```python
# src/expense_tracker/app/gui_v2/views/main_window.py
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFrame, QGraphicsOpacityEffect, QHBoxLayout,
    QMainWindow, QStackedWidget, QVBoxLayout, QWidget,
)

from expense_tracker.app.gui_v2 import tokens
from expense_tracker.app.gui_v2.constants import PageIndex

if TYPE_CHECKING:
    from expense_tracker.app.composition import Services


class MainWindow(QMainWindow):
    """Shell: sidebar + topbar + stacked pages."""

    refresh_requested       = pyqtSignal()
    add_income_requested    = pyqtSignal()
    add_spend_requested     = pyqtSignal()
    add_charge_requested    = pyqtSignal()
    mark_charge_paid_requested = pyqtSignal(str)

    _PAGE_NAMES = {
        "dashboard": "DASHBOARD / 01",
        "activity":  "ACTIVITY / 01",
        "insights":  "INSIGHTS / 01",
        "settings":  "SETTINGS / 01",
    }

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Mizān")
        self.setMinimumSize(1100, 720)

        self._on_page_enter: dict[int, Callable] = {}

        # ── Pages ──────────────────────────────────────────────────
        from expense_tracker.app.gui_v2.views.dashboard_page import DashboardPage
        from expense_tracker.app.gui_v2.views.activity_page import ActivityPage
        from expense_tracker.app.gui_v2.views.insights_page import InsightsPage
        from expense_tracker.app.gui_v2.views.settings_page import SettingsPage

        self.dashboard_page = DashboardPage(
            add_income_signal=self.add_income_requested,
            add_spend_signal=self.add_spend_requested,
            add_charge_signal=self.add_charge_requested,
            mark_charge_paid_signal=self.mark_charge_paid_requested,
        )
        self.activity_page = ActivityPage()
        self.insights_page = InsightsPage()
        self.settings_page = SettingsPage()

        self._stack = QStackedWidget()
        self._stack.addWidget(self.dashboard_page)
        self._stack.addWidget(self.activity_page)
        self._stack.addWidget(self.insights_page)
        self._stack.addWidget(self.settings_page)

        # ── Sidebar / Topbar ────────────────────────────────────────
        from expense_tracker.app.gui_v2.widgets.sidebar import Sidebar
        from expense_tracker.app.gui_v2.widgets.topbar import Topbar

        self._sidebar = Sidebar()
        self._topbar  = Topbar()
        self._sidebar.nav_changed.connect(self._on_nav_changed)
        self._topbar.refresh_requested.connect(self.refresh_requested.emit)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCentralWidget(self._build_root())

    # ── Controller wiring (called from main.py after window is created) ──

    def _wire_controllers(self, services) -> None:
        from decimal import Decimal
        from PyQt6.QtCore import QSettings

        threshold = Decimal(
            QSettings("Mizan", "Mizan").value("balance/cautionThreshold", "100")
        )

        from expense_tracker.app.gui_v2.controllers.dashboard_controller import DashboardController
        self._dash_ctrl = DashboardController(
            view=self,
            session_service=services.session_service,
            balance_service=services.balance_service,
            income_service=services.income_service,
            charge_service=services.charge_service,
            fuzzy_charge_service=services.fuzzy_charge_service,
            spend_service=services.spend_service,
            caution_threshold=threshold,
        )
        self.register_page_enter(PageIndex.DASHBOARD, self._dash_ctrl.refresh)
        self._dash_ctrl.refresh()

    # ── Navigation ───────────────────────────────────────────────────────

    def _on_nav_changed(self, key: str) -> None:
        mapping = {
            "dashboard": PageIndex.DASHBOARD,
            "activity":  PageIndex.ACTIVITY,
            "insights":  PageIndex.INSIGHTS,
            "settings":  PageIndex.SETTINGS,
        }
        idx = mapping.get(key, PageIndex.DASHBOARD)
        self._stack.setCurrentIndex(idx)
        self._topbar.set_breadcrumb(self._PAGE_NAMES.get(key, "DASHBOARD / 01"))
        self._fade_in(self._stack.currentWidget())

        cb = self._on_page_enter.get(idx)
        if cb:
            cb()

    def _fade_in(self, widget: QWidget) -> None:
        """150ms fade-in using QGraphicsOpacityEffect (works on child widgets)."""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", widget)
        anim.setDuration(150)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(lambda: widget.setGraphicsEffect(None))
        anim.start()

    def register_page_enter(self, index: int, callback: Callable) -> None:
        self._on_page_enter[index] = callback

    # ── Public setters (proxy to dashboard_page) ──────────────────────────

    def set_snapshot(self, snapshot, last_sync=None, animate: bool = True) -> None:
        self.dashboard_page.set_snapshot(snapshot, animate=animate)
        self._topbar.set_on_track_state(snapshot.on_track_state_value)
        if last_sync:
            self._topbar.set_last_sync(last_sync.strftime("%d %b · %H:%M"))

    def set_upcoming(self, rows) -> None:
        self.dashboard_page.set_upcoming(rows)

    def set_recent(self, rows) -> None:
        self.dashboard_page.set_recent(rows)

    def set_categories(self, rows) -> None:
        self.dashboard_page.set_categories(rows)

    def set_alert(self, body_html: str, amount_str: str, visible: bool) -> None:
        self.dashboard_page.set_alert(body_html, amount_str, visible)

    # ── Keyboard shortcuts ────────────────────────────────────────────────

    def keyPressEvent(self, event) -> None:
        if event.modifiers() == Qt.KeyboardModifier.AltModifier:
            key_map = {
                Qt.Key.Key_1: "dashboard",
                Qt.Key.Key_2: "activity",
                Qt.Key.Key_3: "insights",
                Qt.Key.Key_4: "settings",
            }
            if event.key() in key_map:
                self._sidebar.navigate_to(key_map[event.key()])
                event.accept()
                return
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_R:
            self.refresh_requested.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    # ── Layout ────────────────────────────────────────────────────────────

    def _build_root(self) -> QWidget:
        root = QWidget()
        root.setObjectName("appRoot")
        h = QHBoxLayout(root)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)
        h.addWidget(self._sidebar)
        divider = QFrame()
        divider.setObjectName("sidebarDivider")
        divider.setFixedWidth(1)
        divider.setStyleSheet(f"background: {tokens.HAIRLINE};")
        h.addWidget(divider)
        h.addWidget(self._build_main_area(), stretch=1)
        return root

    def _build_main_area(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        v.addWidget(self._topbar)
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background: {tokens.HAIRLINE};")
        v.addWidget(divider)
        v.addWidget(self._stack, stretch=1)
        return w
```

- [ ] **Step 3: Create placeholder DashboardPage**

```python
# src/expense_tracker/app/gui_v2/views/dashboard_page.py
from __future__ import annotations
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

class DashboardPage(QWidget):
    """Placeholder — filled in Task 12."""

    def __init__(self, add_income_signal=None, add_spend_signal=None,
                 add_charge_signal=None, mark_charge_paid_signal=None) -> None:
        super().__init__()
        self.setObjectName("dashboardPage")
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Dashboard — building..."))

    def set_snapshot(self, snapshot, animate: bool = True) -> None:
        pass

    def set_upcoming(self, rows) -> None:
        pass

    def set_recent(self, rows) -> None:
        pass

    def set_categories(self, rows) -> None:
        pass

    def set_alert(self, body_html: str, amount_str: str, visible: bool) -> None:
        pass
```

- [ ] **Step 4: Verify the app launches**

```bash
cd /home/dark-vader/PycharmProjects/student-expense-tracker
python -m expense_tracker.app.gui.main
```

Expected: Window opens with placeholder sidebar and topbar. Closing it exits cleanly.

- [ ] **Step 5: Commit**

```bash
git add src/expense_tracker/app/gui_v2/views/
git commit -m "feat(gui_v2): MainWindow shell with placeholder pages"
```

---

## Task 4: Sidebar widget

**Files:**
- Create: `src/expense_tracker/app/gui_v2/widgets/__init__.py`
- Create: `src/expense_tracker/app/gui_v2/widgets/sidebar.py`

- [ ] **Step 1: Create sidebar.py**

```python
# src/expense_tracker/app/gui_v2/widgets/sidebar.py
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton,
    QVBoxLayout, QWidget,
)

from expense_tracker.app.gui_v2 import fonts, tokens
from expense_tracker.app.gui_v2.constants import PageIndex


class Sidebar(QWidget):
    """Left navigation panel. Emits nav_changed(key) on navigation."""

    nav_changed = pyqtSignal(str)

    _NAV_ITEMS = [
        ("dashboard", "Dashboard"),
        ("activity",  "Activity"),
        ("insights",  "Insights"),
        ("settings",  "Settings"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(tokens.SIDEBAR_W)
        self._active_key = "dashboard"
        self._nav_buttons: dict[str, QPushButton] = {}
        self._build()

    def navigate_to(self, key: str) -> None:
        """Programmatic navigation (e.g. from keyboard shortcut)."""
        if key in self._nav_buttons:
            self._on_nav_clicked(key)

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_brand())
        layout.addWidget(self._build_nav(), stretch=1)
        layout.addWidget(self._build_user())

    def _build_brand(self) -> QWidget:
        w = QWidget()
        w.setObjectName("sbBrand")
        w.setStyleSheet(f"QWidget#sbBrand {{ border-bottom: 1px solid {tokens.HAIRLINE}; }}")
        v = QVBoxLayout(w)
        v.setContentsMargins(20, 18, 20, 14)
        v.setSpacing(2)

        top = QHBoxLayout()
        tag = QLabel("STUDENT BUDGET")
        tag.setObjectName("sbTag")
        ver = QLabel("v2")
        ver.setObjectName("sbTag")
        top.addWidget(tag)
        top.addStretch()
        top.addWidget(ver)
        v.addLayout(top)

        wordmark = QLabel("ميزان")
        wordmark.setObjectName("sbWordmark")
        wordmark.setFont(fonts.arabic(25))
        wordmark.setAlignment(Qt.AlignmentFlag.AlignRight)
        v.addWidget(wordmark)

        sub = QHBoxLayout()
        mizan_lbl = QLabel("MIZĀN")
        mizan_lbl.setObjectName("sbTag")
        sub.addWidget(mizan_lbl)
        sub.addStretch()
        v.addLayout(sub)

        return w

    def _build_nav(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 8, 0, 8)
        v.setSpacing(0)

        sec = QLabel("MAIN")
        sec.setObjectName("sbTag")
        sec.setContentsMargins(20, 9, 0, 3)
        v.addWidget(sec)

        for key, label in self._NAV_ITEMS:
            btn = QPushButton(f"  {label}")
            btn.setObjectName("navItem")
            btn.setFixedHeight(33)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self._on_nav_clicked(k))
            self._nav_buttons[key] = btn
            v.addWidget(btn)

        v.addWidget(self._build_streak())
        v.addStretch()
        return w

    def _build_streak(self) -> QWidget:
        w = QWidget()
        w.setObjectName("streakBox")
        w.setContentsMargins(14, 6, 14, 8)
        v = QVBoxLayout(w)
        v.setContentsMargins(12, 9, 12, 9)
        v.setSpacing(6)

        hdr = QHBoxLayout()
        lbl = QLabel("STREAK")
        lbl.setObjectName("streakLabel")
        count = QLabel()
        count.setObjectName("streakLabel")
        count.setText("0 days")
        hdr.addWidget(lbl)
        hdr.addStretch()
        hdr.addWidget(count)
        v.addLayout(hdr)

        # 7 segment bars
        segs = QHBoxLayout()
        segs.setSpacing(3)
        for i in range(7):
            seg = QFrame()
            seg.setFixedHeight(6)
            seg.setStyleSheet(
                f"background: {tokens.GOLD}; border-radius: 3px;"
                if i < 3  # placeholder: first 3 active
                else f"background: {tokens.HAIRLINE}; border-radius: 3px;"
            )
            segs.addWidget(seg)
        v.addLayout(segs)
        return w

    def _build_user(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"border-top: 1px solid {tokens.HAIRLINE};")
        h = QHBoxLayout(w)
        h.setContentsMargins(20, 12, 20, 12)
        h.setSpacing(11)

        avatar = QLabel("S")
        avatar.setFixedSize(33, 33)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFont(fonts.label(tokens.T_XS))
        avatar.setStyleSheet(
            f"background: {tokens.NAVY}; color: {tokens.GOLD}; "
            f"border-radius: 16px; font-family: 'DM Mono';"
        )
        h.addWidget(avatar)

        info = QVBoxLayout()
        info.setSpacing(1)
        name = QLabel("Student")
        name.setFont(fonts.label(tokens.T_SM))
        name.setStyleSheet(f"color: {tokens.FG}; background: transparent;")
        sub = QLabel("Academic Year")
        sub.setFont(fonts.label(tokens.T_MINI))
        sub.setStyleSheet(f"color: {tokens.MUTED}; background: transparent;")
        info.addWidget(name)
        info.addWidget(sub)
        h.addLayout(info)
        return w

    def _on_nav_clicked(self, key: str) -> None:
        if key == self._active_key:
            return
        # Deactivate old
        old = self._nav_buttons.get(self._active_key)
        if old:
            old.setProperty("active", False)
            old.style().unpolish(old)
            old.style().polish(old)
        # Activate new
        self._active_key = key
        btn = self._nav_buttons[key]
        btn.setProperty("active", True)
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        self.nav_changed.emit(key)

    def _activate_initial(self) -> None:
        btn = self._nav_buttons.get("dashboard")
        if btn:
            btn.setProperty("active", True)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._activate_initial()
```

- [ ] **Step 2: Run and verify sidebar renders**

```bash
python -m expense_tracker.app.gui.main
```

Expected: Sidebar shows brand block with Arabic wordmark, 4 nav items, streak box, user block. Clicking nav items highlights them.

- [ ] **Step 3: Commit**

```bash
git add src/expense_tracker/app/gui_v2/widgets/
git commit -m "feat(gui_v2): Sidebar widget with nav, streak, user block"
```

---

## Task 5: Topbar widget

**Files:**
- Modify: `src/expense_tracker/app/gui_v2/widgets/topbar.py` (create)

- [ ] **Step 1: Create topbar.py**

```python
# src/expense_tracker/app/gui_v2/widgets/topbar.py
from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame, QGraphicsOpacityEffect, QHBoxLayout, QLabel,
    QPushButton, QWidget,
)

from expense_tracker.app.gui_v2 import fonts, tokens


class _PulseDot(QWidget):
    """7px pulsing dot for the status pill (replaces CSS @keyframes)."""

    def __init__(self, color: str, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(7, 7)
        self._color = color
        self.setStyleSheet(
            f"background: {color}; border-radius: 3px;"
        )
        self._effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._effect)
        self._anim = QPropertyAnimation(self._effect, b"opacity", self)
        self._anim.setDuration(1200)
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.2)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._anim.setLoopCount(-1)
        self._anim.start()

    def set_color(self, color: str) -> None:
        self._color = color
        self.setStyleSheet(f"background: {color}; border-radius: 3px;")


class _StatusPill(QWidget):
    """On-track status pill with pulse dot."""

    _STATE_COLORS = {
        "green":       tokens.GREEN,
        "yellow":      tokens.AMBER,
        "red":         tokens.RED,
        "tight_month": tokens.AMBER,
    }
    _STATE_LABELS = {
        "green":       "ON TRACK",
        "yellow":      "CAUTION",
        "red":         "OVERSPENT",
        "tight_month": "TIGHT",
    }

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("statusPill")

        self._dot = _PulseDot(tokens.GREEN)
        self._label = QLabel("ON TRACK")
        self._label.setObjectName("pillText")
        self._label.setFont(fonts.label(tokens.T_XS))

        h = QHBoxLayout(self)
        h.setContentsMargins(10, 4, 12, 4)
        h.setSpacing(6)
        h.addWidget(self._dot)
        h.addWidget(self._label)

        self.set_state("green")

    def set_state(self, state: str) -> None:
        color = self._STATE_COLORS.get(state, tokens.GREEN)
        text  = self._STATE_LABELS.get(state, "ON TRACK")
        self._dot.set_color(color)
        self._label.setText(text)

        self.setProperty("state", state if state in ("green", "amber", "red") else "amber")
        self._label.setProperty("state", state if state in ("green", "amber", "red") else "amber")
        for w in (self, self._label):
            w.style().unpolish(w)
            w.style().polish(w)


class Topbar(QWidget):
    """Sticky topbar with breadcrumb, status pill, sync button, bell."""

    refresh_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("topbar")
        self.setFixedHeight(tokens.TOPBAR_H)

        self._status_pill = _StatusPill()
        self._bc_label    = QLabel("DASHBOARD")
        self._date_label  = QLabel()
        self._sync_btn    = QPushButton("↺  SYNC")
        self._bell_btn    = QPushButton("🔔")

        self._bc_label.setObjectName("tbBcLabel")
        self._date_label.setObjectName("tbDate")
        self._sync_btn.setObjectName("tbSync")
        self._bell_btn.setObjectName("tbBell")
        self._bell_btn.setFixedSize(28, 28)
        self._sync_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._bell_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self._sync_btn.clicked.connect(self.refresh_requested.emit)
        self._update_date()

        # Refresh date label every minute
        timer = QTimer(self)
        timer.timeout.connect(self._update_date)
        timer.start(60_000)

        self._build()

    def set_breadcrumb(self, text: str) -> None:
        self._bc_label.setText(text)

    def set_on_track_state(self, state: str) -> None:
        self._status_pill.set_state(state)

    def set_last_sync(self, text: str) -> None:
        self._sync_btn.setToolTip(f"Last sync: {text}")

    def _update_date(self) -> None:
        self._date_label.setText(datetime.now().strftime("%d %b %Y"))

    def _build(self) -> None:
        h = QHBoxLayout(self)
        h.setContentsMargins(tokens.CONTENT_PAD, 0, tokens.CONTENT_PAD, 0)
        h.setSpacing(14)

        # Breadcrumb block
        bc = QWidget()
        bv = QWidget()
        bvl = QWidget.__init__  # just a container
        from PyQt6.QtWidgets import QVBoxLayout as VBL
        bcl = VBL(bc)
        bcl.setContentsMargins(0, 0, 0, 0)
        bcl.setSpacing(1)
        bcl.addWidget(self._bc_label)
        bcl.addWidget(self._date_label)

        h.addWidget(bc)
        h.addStretch()
        h.addWidget(self._status_pill)
        h.addWidget(self._sync_btn)
        h.addWidget(self._bell_btn)
```

- [ ] **Step 2: Run and verify topbar renders**

```bash
python -m expense_tracker.app.gui.main
```

Expected: Topbar shows breadcrumb "DASHBOARD", today's date, pulsing green status pill, sync button, bell button.

- [ ] **Step 3: Commit**

```bash
git add src/expense_tracker/app/gui_v2/widgets/topbar.py
git commit -m "feat(gui_v2): Topbar with status pulse pill and sync button"
```

---

## Task 6: HeroCard

**Files:**
- Create: `src/expense_tracker/app/gui_v2/widgets/hero_card.py`

- [ ] **Step 1: Create hero_card.py**

```python
# src/expense_tracker/app/gui_v2/widgets/hero_card.py
"""
Hero card — the "FREE MONEY" display.

The gradient background is drawn entirely in paintEvent (CSS3 radial-gradient
is not reliably supported in Qt QSS). The border-color is controlled by QSS
via setProperty("balanceState", state) — see stylesheet.py heroCard rules.
"""
from __future__ import annotations

import calendar
from datetime import datetime
from decimal import Decimal

from PyQt6.QtCore import QEasingCurve, QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor, QLinearGradient, QPainter, QPen, QRadialGradient,
)
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from expense_tracker.app.gui_v2 import fonts, tokens
from expense_tracker.app.gui_v2.widgets.counting_label import CountingLabel

# rgba tint for the hero card radial gradient
_HERO_TINT = QColor(252, 247, 234, 62)

_STATES = {
    "normal":  {"border": tokens.GOLD,  "badge": "ON TRACK",  "badge_bg": "rgba(199,154,57,0.12)",  "badge_fg": tokens.GOLD_LEAF},
    "caution": {"border": tokens.AMBER, "badge": "CAUTION",   "badge_bg": "rgba(245,158,11,0.12)",  "badge_fg": tokens.AMBER},
    "crisis":  {"border": tokens.RED,   "badge": "OVERSPENT", "badge_bg": "rgba(150,46,46,0.12)",   "badge_fg": tokens.RED},
}


class HeroCard(QFrame):
    """Main free-money card. Gradient painted; border driven by QSS property."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("heroCard")
        self.setMinimumHeight(200)
        self.setProperty("balanceState", "normal")

        # ── Money display ──────────────────────────────────────────────
        self._sym_label = QLabel("₪")
        self._sym_label.setObjectName("moneySym")
        self._sym_label.setFont(fonts.money(22, 400))

        self._money_label = CountingLabel("{:,.0f}")
        self._money_label.setObjectName("moneyValue")
        self._money_label.setFont(fonts.money(52))

        money_row = QHBoxLayout()
        money_row.setContentsMargins(0, 0, 0, 0)
        money_row.setSpacing(2)
        money_row.addWidget(self._sym_label, alignment=Qt.AlignmentFlag.AlignBottom)
        money_row.addWidget(self._money_label, alignment=Qt.AlignmentFlag.AlignBottom)
        money_row.addStretch()

        # ── State badge ────────────────────────────────────────────────
        self._badge = QLabel("ON TRACK")
        self._badge.setObjectName("stateBadge")
        self._badge.setProperty("state", "normal")
        self._badge.setFont(fonts.label_bold(tokens.T_MINI))

        # ── Labels (free money / period) ───────────────────────────────
        self._mini_label = QLabel("FREE MONEY")
        self._mini_label.setObjectName("heroMiniLabel")
        self._mini_label.setFont(fonts.label(tokens.T_MINI))

        self._sub_label = QLabel("after all upcoming charges")
        self._sub_label.setObjectName("heroSubLabel")
        self._sub_label.setFont(fonts.label(tokens.T_MINI))

        # ── Timeline (imported lazily to avoid circular) ───────────────
        from expense_tracker.app.gui_v2.widgets.timeline_widget import TimelineWidget
        self.timeline = TimelineWidget()

        # ── Legend ────────────────────────────────────────────────────
        self._legend = QLabel()
        self._legend.setObjectName("heroSubLabel")
        self._legend.setFont(fonts.label(tokens.T_SM))
        self._legend.setWordWrap(True)

        # ── Layout ────────────────────────────────────────────────────
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 16)
        root.setSpacing(6)
        root.addWidget(self._mini_label)
        root.addWidget(self._sub_label)
        root.addLayout(money_row)
        root.addWidget(self._badge)
        root.addWidget(self._legend)
        root.addWidget(self.timeline)

    # ── Public API ────────────────────────────────────────────────────────

    def set_money_value(self, value: Decimal, animate: bool = True) -> None:
        self._money_label.set_value(value, animate=animate)

    def set_state(self, state: str) -> None:
        cfg = _STATES.get(state, _STATES["normal"])
        self._badge.setText(cfg["badge"])
        # Update QSS property (triggers border-color change in stylesheet.py)
        self.setProperty("balanceState", state)
        self._badge.setProperty("state", state)
        for w in (self, self._badge):
            w.style().unpolish(w)
            w.style().polish(w)

    def set_legend(self, spent: str, committed: str, fuzzy: str, budget: str) -> None:
        self._legend.setText(
            f"Spent ₪{spent}  ·  Committed ₪{committed}  ·  Fuzzy ₪{fuzzy}  ·  Budget ₪{budget}"
        )

    def set_period_for_today(self) -> None:
        today = datetime.now()
        self._mini_label.setText(
            f"FREE MONEY · {today.strftime('%B %Y').upper()}"
        )

    def set_daily_allowance(self, amount_str: str, _: str) -> None:
        pass  # surfaced in StatColumn instead

    def set_alert(self, body_html: str, amount_str: str, visible: bool) -> None:
        pass  # alert is in AlertBanner, not HeroCard

    # ── Gradient background (paintEvent) ─────────────────────────────────

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        radius = tokens.CARD_RADIUS

        # Clip to rounded rect
        from PyQt6.QtGui import QPainterPath
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        painter.setClipPath(path)

        # Layer 1: linear gradient base
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0.0, QColor(tokens.HERO_BG1))
        grad.setColorAt(1.0, QColor(tokens.HERO_BG2))
        painter.fillRect(rect, grad)

        # Layer 2: radial tint top-right
        r1 = QRadialGradient(QPointF(rect.right() * 0.88, rect.top()), rect.width() * 0.5)
        r1.setColorAt(0.0, _HERO_TINT)
        r1.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(rect, r1)

        # Layer 3: dot grain texture (3×3 pattern)
        grain = QColor(120, 110, 90, 13)
        painter.setPen(QPen(grain, 1))
        for x in range(0, int(rect.width()), 3):
            for y in range(0, int(rect.height()), 3):
                painter.drawPoint(x, y)

        painter.end()

        # Let QFrame draw the border on top
        super().paintEvent(event)
```

- [ ] **Step 2: Run and verify hero card renders**

```bash
python -m expense_tracker.app.gui.main
```

Expected: HeroCard renders with warm gradient background, "FREE MONEY" label, ₪0 in Playfair Display, gold border.

- [ ] **Step 3: Commit**

```bash
git add src/expense_tracker/app/gui_v2/widgets/hero_card.py
git commit -m "feat(gui_v2): HeroCard with paintEvent gradient and state system"
```

---

## Task 7: TimelineWidget and CountingLabel

**Files:**
- Create: `src/expense_tracker/app/gui_v2/widgets/counting_label.py`
- Create: `src/expense_tracker/app/gui_v2/widgets/timeline_widget.py`

- [ ] **Step 1: Copy and clean CountingLabel**

```python
# src/expense_tracker/app/gui_v2/widgets/counting_label.py
from __future__ import annotations

from decimal import Decimal

from PyQt6.QtCore import QEasingCurve, QVariantAnimation
from PyQt6.QtWidgets import QLabel


class CountingLabel(QLabel):
    """QLabel that animates between numeric values with a count-up/down effect."""

    def __init__(self, fmt: str = "{:,.0f}", parent=None) -> None:
        super().__init__(parent)
        self._fmt = fmt
        self._value = 0.0
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(600)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._on_tick)
        self.setText(fmt.format(0.0))

    def set_value(self, value: Decimal, animate: bool = True) -> None:
        target = float(value)
        if not animate or self._value == target:
            self._anim.stop()
            self._value = target
            self.setText(self._fmt.format(target))
            return
        self._anim.stop()
        self._anim.setStartValue(self._value)
        self._anim.setEndValue(target)
        self._anim.start()
        self._value = target

    def _on_tick(self, v: float) -> None:
        self.setText(self._fmt.format(v))
```

- [ ] **Step 2: Copy TimelineWidget from old GUI, update tokens import**

```bash
cp src/expense_tracker/app/gui/widgets/timeline_widget.py \
   src/expense_tracker/app/gui_v2/widgets/timeline_widget.py
```

Then open `src/expense_tracker/app/gui_v2/widgets/timeline_widget.py` and change the two imports at the top from:

```python
from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.styles.theme_manager import get_theme_manager
```

to:

```python
from expense_tracker.app.gui_v2 import tokens
```

Remove any reference to `get_theme_manager()` and replace `get_theme_manager().get_color(...)` calls with the direct `tokens.*` equivalents (e.g., `tokens.AMBER`, `tokens.GOLD_LEAF`).

- [ ] **Step 3: Commit**

```bash
git add src/expense_tracker/app/gui_v2/widgets/counting_label.py \
        src/expense_tracker/app/gui_v2/widgets/timeline_widget.py
git commit -m "feat(gui_v2): CountingLabel and TimelineWidget (cleaned)"
```

---

## Task 8: AlertBanner and StatColumn

**Files:**
- Create: `src/expense_tracker/app/gui_v2/widgets/alert_banner.py`
- Create: `src/expense_tracker/app/gui_v2/widgets/stat_column.py`

- [ ] **Step 1: Create alert_banner.py**

```python
# src/expense_tracker/app/gui_v2/widgets/alert_banner.py
from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel


class AlertBanner(QFrame):
    """Amber warning strip shown when fuzzy charges are pending."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("alertBanner")
        self.hide()

        self._badge = QLabel("HEADS UP")
        self._badge.setObjectName("alertBadge")

        self._body = QLabel()
        self._body.setObjectName("alertBody")
        self._body.setWordWrap(True)

        self._amt = QLabel()
        self._amt.setObjectName("alertAmt")

        h = QHBoxLayout(self)
        h.setContentsMargins(16, 9, 16, 9)
        h.setSpacing(12)
        h.addWidget(self._badge)
        h.addWidget(self._body, stretch=1)
        h.addWidget(self._amt)

    def set_alert(self, body_html: str, amount_str: str, visible: bool) -> None:
        self._body.setText(body_html)
        self._amt.setText(amount_str)
        self.setVisible(visible)
```

- [ ] **Step 2: Create stat_column.py**

```python
# src/expense_tracker/app/gui_v2/widgets/stat_column.py
from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from expense_tracker.app.gui_v2 import fonts, tokens

if TYPE_CHECKING:
    from expense_tracker.app.gui_v2.view_models.balance_view_model import BalanceViewModel


def _stat_card(micro: str, value_str: str, value_color: str,
               sub_str: str = "") -> QFrame:
    card = QFrame()
    card.setObjectName("card")
    v = QVBoxLayout(card)
    v.setContentsMargins(16, 14, 16, 14)
    v.setSpacing(2)

    lbl = QLabel(micro.upper())
    lbl.setObjectName("cardMicro")
    v.addWidget(lbl)

    val = QLabel(f"₪{value_str}")
    val.setFont(fonts.money_sm(28))
    val.setStyleSheet(f"color: {value_color}; background: transparent;")
    v.addWidget(val)

    if sub_str:
        sub = QLabel(sub_str)
        sub.setObjectName("cardMeta")
        v.addWidget(sub)

    return card


class StatColumn(QWidget):
    """Right column of 4 stat cards: Spent, Committed, Income, Daily Allowance."""

    def __init__(self) -> None:
        super().__init__()
        self.setFixedWidth(tokens.STAT_COL_W)

        self._spent_card     = _stat_card("Total Spent",     "0",  tokens.GOLD_LEAF)
        self._committed_card = _stat_card("Committed",        "0",  tokens.RED)
        self._income_card    = _stat_card("Income",           "0",  tokens.GREEN)
        self._allowance_card = _stat_card("Daily Allowance",  "0",  tokens.GREEN)

        # Keep value labels accessible for updates
        self._spent_val     = self._spent_card.findChild(QLabel,     "", )
        self._committed_val = self._committed_card.findChild(QLabel, "", )
        self._income_val    = self._income_card.findChild(QLabel,    "", )
        self._allowance_val = self._allowance_card.findChild(QLabel, "", )

        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)
        v.addWidget(self._spent_card)
        v.addWidget(self._committed_card)
        v.addWidget(self._income_card)
        v.addWidget(self._allowance_card, stretch=1)

    def set_snapshot(self, vm: BalanceViewModel, animate: bool = True) -> None:
        def _update_val(card: QFrame, text: str) -> None:
            for lbl in card.findChildren(QLabel):
                if lbl.objectName() == "":  # the value label has no objectName
                    lbl.setText(f"₪{text}")
                    return

        _update_val(self._spent_card,     vm.monthly_spent_str)
        _update_val(self._committed_card, vm.monthly_committed_str)
        _update_val(self._income_card,    vm.monthly_budget_str)
        _update_val(self._allowance_card, vm.monthly_left_str)
```

- [ ] **Step 3: Commit**

```bash
git add src/expense_tracker/app/gui_v2/widgets/alert_banner.py \
        src/expense_tracker/app/gui_v2/widgets/stat_column.py
git commit -m "feat(gui_v2): AlertBanner and StatColumn widgets"
```

---

## Task 9: Panels (Category, Upcoming, Recent)

**Files:**
- Create: `src/expense_tracker/app/gui_v2/widgets/panels.py`

- [ ] **Step 1: Define row view models**

```python
# src/expense_tracker/app/gui_v2/widgets/panels.py
from __future__ import annotations

from dataclasses import dataclass
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)

from expense_tracker.app.gui_v2 import fonts, tokens


@dataclass(frozen=True)
class CategoryRowVM:
    name: str
    amount_str: str
    pct: float          # 0.0 – 1.0
    color: str          # hex color string


@dataclass(frozen=True)
class ChargeRowVM:
    charge_id: str
    name: str
    amount_str: str
    due_date_str: str
    timing_str: str     # "in 3 days", "overdue"
    is_urgent: bool     # due within 7 days
    is_fuzzy: bool


@dataclass(frozen=True)
class TxRowVM:
    description: str
    category_str: str
    amount_str: str
    is_income: bool
    date_str: str


def _panel(title: str, meta: str, action_label: str,
           action_signal: pyqtSignal | None = None) -> tuple[QFrame, QVBoxLayout, QPushButton]:
    """Build a panel card and return (card, content_layout, action_button)."""
    card = QFrame()
    card.setObjectName("card")
    root = QVBoxLayout(card)
    root.setContentsMargins(18, 16, 18, 16)
    root.setSpacing(0)

    # Header
    hdr = QHBoxLayout()
    title_lbl = QLabel(title)
    title_lbl.setObjectName("cardTitle")
    title_lbl.setFont(fonts.label_bold(tokens.T_SM))
    meta_lbl = QLabel(meta)
    meta_lbl.setObjectName("cardMeta")
    meta_lbl.setFont(fonts.label(tokens.T_SM))
    action_btn = QPushButton(action_label)
    action_btn.setObjectName("linkBtn")
    action_btn.setFont(fonts.label(tokens.T_SM))
    action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    if action_signal is not None:
        action_btn.clicked.connect(action_signal.emit)

    hdr.addWidget(title_lbl)
    hdr.addWidget(meta_lbl)
    hdr.addStretch()
    hdr.addWidget(action_btn)
    root.addLayout(hdr)

    # Divider
    div = QFrame()
    div.setFixedHeight(1)
    div.setStyleSheet(f"background: {tokens.HAIRLINE}; margin: 8px 0 11px 0;")
    root.addWidget(div)

    # Content area (scroll)
    content_w = QWidget()
    content_l = QVBoxLayout(content_w)
    content_l.setContentsMargins(0, 0, 0, 0)
    content_l.setSpacing(0)

    scroll = QScrollArea()
    scroll.setWidget(content_w)
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    root.addWidget(scroll, stretch=1)

    return card, content_l, action_btn


def _clear_layout(layout: QVBoxLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()


# ── CategoryPanel ─────────────────────────────────────────────────────────────

class CategoryPanel(QWidget):
    def __init__(self, add_income_signal=None) -> None:
        super().__init__()
        self._card, self._content, _ = _panel(
            "SPENDING", "this month", "+ Income", add_income_signal
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._card)

    def set_categories(self, rows: list[CategoryRowVM]) -> None:
        _clear_layout(self._content)
        if not rows:
            lbl = QLabel("No spend recorded yet")
            lbl.setObjectName("emptyState")
            self._content.addWidget(lbl)
            return
        for row in rows:
            self._content.addWidget(self._make_row(row))
        self._content.addStretch()

    def _make_row(self, row: CategoryRowVM) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 11)
        v.setSpacing(5)

        top = QHBoxLayout()
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {row.color}; background: transparent;")
        name = QLabel(row.name.capitalize())
        name.setObjectName("cardTitle")
        name.setFont(fonts.label(tokens.T_BASE))
        pct_lbl = QLabel(f"{row.pct * 100:.0f}%")
        pct_lbl.setObjectName("cardMeta")
        amt = QLabel(f"₪{row.amount_str}")
        amt.setFont(fonts.money_sm(13))
        amt.setStyleSheet(f"color: {tokens.FG}; background: transparent;")
        top.addWidget(dot)
        top.addWidget(name)
        top.addWidget(pct_lbl)
        top.addStretch()
        top.addWidget(amt)
        v.addLayout(top)

        bar_bg = QFrame()
        bar_bg.setFixedHeight(5)
        bar_bg.setStyleSheet(
            f"background: {tokens.TRACK}; border-radius: 2px;"
        )
        bar_fill = QFrame(bar_bg)
        bar_fill.setFixedHeight(5)
        bar_fill.setFixedWidth(max(4, int(row.pct * (tokens.STAT_COL_W - 36))))
        bar_fill.setStyleSheet(
            f"background: {row.color}; border-radius: 2px;"
        )
        v.addWidget(bar_bg)
        return w


# ── UpcomingPanel ─────────────────────────────────────────────────────────────

class UpcomingPanel(QWidget):
    charge_paid = pyqtSignal(str)

    def __init__(self, add_charge_signal=None) -> None:
        super().__init__()
        self._card, self._content, _ = _panel(
            "UPCOMING", "this month", "+ Charge", add_charge_signal
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._card)

    def set_upcoming(self, rows: list[ChargeRowVM]) -> None:
        _clear_layout(self._content)
        if not rows:
            lbl = QLabel("No upcoming charges")
            lbl.setObjectName("emptyState")
            self._content.addWidget(lbl)
            return
        for row in rows:
            self._content.addWidget(self._make_row(row))
        self._content.addStretch()

    def _make_row(self, row: ChargeRowVM) -> QWidget:
        stripe_color = tokens.RED if row.is_urgent else (tokens.AMBER if row.is_fuzzy else tokens.MUTED)
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 9, 0, 9)
        h.setSpacing(11)

        stripe = QFrame()
        stripe.setFixedWidth(4)
        stripe.setStyleSheet(f"background: {stripe_color}; border-radius: 2px;")

        body = QWidget()
        bv = QVBoxLayout(body)
        bv.setContentsMargins(0, 0, 0, 0)
        bv.setSpacing(1)
        name_row = QHBoxLayout()
        name_lbl = QLabel(row.name)
        name_lbl.setObjectName("cardTitle")
        name_lbl.setFont(fonts.label(tokens.T_BASE))
        name_row.addWidget(name_lbl)
        bv.addLayout(name_row)
        date_lbl = QLabel(f"{row.due_date_str}  ·  {row.timing_str}")
        date_lbl.setObjectName("cardMeta")
        bv.addWidget(date_lbl)

        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(2)
        color = tokens.AMBER if row.is_fuzzy else (tokens.RED if row.is_urgent else tokens.MUTED_FG)
        amt = QLabel(f"₪{row.amount_str}" if not row.is_fuzzy else "~?")
        amt.setFont(fonts.money_sm(13))
        amt.setStyleSheet(f"color: {color}; background: transparent;")
        pay_btn = QPushButton("✓")
        pay_btn.setObjectName("linkBtn")
        pay_btn.setFixedSize(24, 24)
        pay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pay_btn.clicked.connect(lambda _, cid=row.charge_id: self.charge_paid.emit(cid))
        rv.addWidget(amt)
        rv.addWidget(pay_btn, alignment=Qt.AlignmentFlag.AlignRight)

        h.addWidget(stripe)
        h.addWidget(body, stretch=1)
        h.addWidget(right)
        return w


# ── RecentPanel ───────────────────────────────────────────────────────────────

class RecentPanel(QWidget):
    def __init__(self, add_spend_signal=None) -> None:
        super().__init__()
        self._card, self._content, _ = _panel(
            "RECENT", "last 7 days", "+ Spend", add_spend_signal
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._card)

    def set_recent(self, rows: list[TxRowVM]) -> None:
        _clear_layout(self._content)
        if not rows:
            lbl = QLabel("No transactions yet")
            lbl.setObjectName("emptyState")
            self._content.addWidget(lbl)
            return
        for row in rows:
            self._content.addWidget(self._make_row(row))
        self._content.addStretch()

    def _make_row(self, row: TxRowVM) -> QWidget:
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 8, 0, 8)
        h.setSpacing(10)

        icon_tile = QFrame()
        icon_tile.setFixedSize(30, 30)
        icon_tile.setStyleSheet(
            f"background: {tokens.SURFACE}; border: 1px solid {tokens.HAIRLINE_S}; border-radius: 8px;"
        )

        body = QWidget()
        bv = QVBoxLayout(body)
        bv.setContentsMargins(0, 0, 0, 0)
        bv.setSpacing(1)
        name = QLabel(row.description[:30])
        name.setObjectName("cardTitle")
        name.setFont(fonts.label(tokens.T_SM))
        meta = QLabel(f"{row.category_str}  ·  {row.date_str}")
        meta.setObjectName("cardMeta")
        bv.addWidget(name)
        bv.addWidget(meta)

        color = tokens.GREEN if row.is_income else tokens.FG
        sign  = "+" if row.is_income else ""
        amt = QLabel(f"{sign}₪{row.amount_str}")
        amt.setFont(fonts.money_sm(13))
        amt.setStyleSheet(f"color: {color}; background: transparent;")

        h.addWidget(icon_tile)
        h.addWidget(body, stretch=1)
        h.addWidget(amt)
        return w
```

- [ ] **Step 2: Commit**

```bash
git add src/expense_tracker/app/gui_v2/widgets/panels.py
git commit -m "feat(gui_v2): CategoryPanel, UpcomingPanel, RecentPanel with view models"
```

---

## Task 10: DashboardPage layout + BalanceViewModel

**Files:**
- Modify: `src/expense_tracker/app/gui_v2/views/dashboard_page.py` (replace placeholder)
- Create: `src/expense_tracker/app/gui_v2/view_models/__init__.py`
- Create: `src/expense_tracker/app/gui_v2/view_models/balance_view_model.py`
- Create: `tests/unit/gui_v2/__init__.py`
- Create: `tests/unit/gui_v2/test_balance_view_model.py`

- [ ] **Step 1: Copy BalanceViewModel (no changes needed)**

```bash
mkdir -p src/expense_tracker/app/gui_v2/view_models
touch src/expense_tracker/app/gui_v2/view_models/__init__.py
cp src/expense_tracker/app/gui/view_models/balance_view_model.py \
   src/expense_tracker/app/gui_v2/view_models/balance_view_model.py
cp src/expense_tracker/app/gui/view_models/ledger_view_model.py \
   src/expense_tracker/app/gui_v2/view_models/ledger_view_model.py
```

- [ ] **Step 2: Write BalanceViewModel tests**

```python
# tests/unit/gui_v2/test_balance_view_model.py
from decimal import Decimal
from expense_tracker.app.gui_v2.view_models.balance_view_model import BalanceViewModel

def _make_vm(**overrides):
    defaults = dict(
        free_money=Decimal("1234.56"),
        free_money_str="1,234.56",
        balance_state_value="normal",
        monthly_budget=Decimal("2000"),
        monthly_budget_str="2,000.00",
        monthly_spent=Decimal("500"),
        monthly_spent_str="500.00",
        monthly_committed=Decimal("800"),
        monthly_committed_str="800.00",
        monthly_fuzzy_estimated=Decimal("0"),
        monthly_fuzzy_estimated_str="0.00",
        monthly_left=Decimal("700"),
        monthly_left_str="700.00",
        on_track_state_value="green",
        timeline_spent_pct=25.0,
        timeline_committed_pct=40.0,
        timeline_fuzzy_left_pct=0.0,
        timeline_fuzzy_width_pct=0.0,
        today_pct=50.0,
    )
    defaults.update(overrides)
    return BalanceViewModel(**defaults)


def test_free_money_is_decimal():
    vm = _make_vm()
    assert vm.free_money == Decimal("1234.56")


def test_balance_state_normal():
    vm = _make_vm(balance_state_value="normal")
    assert vm.balance_state_value == "normal"


def test_balance_state_crisis():
    vm = _make_vm(free_money=Decimal("-50"), balance_state_value="crisis")
    assert vm.balance_state_value == "crisis"


def test_timeline_percentages_sum_reasonable():
    vm = _make_vm(timeline_spent_pct=25.0, timeline_committed_pct=40.0)
    assert vm.timeline_spent_pct + vm.timeline_committed_pct <= 100.0
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/unit/gui_v2/test_balance_view_model.py -v
```

Expected: 4 tests pass.

- [ ] **Step 4: Replace DashboardPage placeholder with real layout**

```python
# src/expense_tracker/app/gui_v2/views/dashboard_page.py
from __future__ import annotations

import calendar
from datetime import datetime
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QScrollArea,
    QVBoxLayout, QWidget,
)

from expense_tracker.app.gui_v2 import tokens
from expense_tracker.app.gui_v2.widgets.alert_banner import AlertBanner
from expense_tracker.app.gui_v2.widgets.hero_card import HeroCard
from expense_tracker.app.gui_v2.widgets.panels import (
    CategoryPanel, CategoryRowVM, ChargeRowVM, RecentPanel,
    TxRowVM, UpcomingPanel,
)
from expense_tracker.app.gui_v2.widgets.stat_column import StatColumn

if TYPE_CHECKING:
    from expense_tracker.app.gui_v2.view_models.balance_view_model import BalanceViewModel


class DashboardPage(QWidget):
    """
    Full dashboard: alert banner + hero row (hero card + stat column) + 3 panels.
    Receives data via set_* methods. Emits nothing — signals proxied through MainWindow.
    """

    def __init__(self, add_income_signal=None, add_spend_signal=None,
                 add_charge_signal=None, mark_charge_paid_signal=None) -> None:
        super().__init__()
        self.setObjectName("dashboardPage")

        self._hero    = HeroCard()
        self._stats   = StatColumn()
        self._alert   = AlertBanner()
        self._cat     = CategoryPanel(add_income_signal)
        self._upcoming = UpcomingPanel(add_charge_signal)
        self._recent  = RecentPanel(add_spend_signal)

        if mark_charge_paid_signal is not None:
            self._upcoming.charge_paid.connect(mark_charge_paid_signal)

        self._build_layout()

    # ── Public setters ────────────────────────────────────────────────────

    def set_snapshot(self, vm: BalanceViewModel, animate: bool = True) -> None:
        self._hero.set_money_value(vm.free_money, animate=animate)
        self._hero.set_state(vm.balance_state_value)
        self._hero.set_period_for_today()
        self._hero.set_legend(
            vm.monthly_spent_str,
            vm.monthly_committed_str,
            vm.monthly_fuzzy_estimated_str,
            vm.monthly_budget_str,
        )
        self._hero.timeline.set_percentages(
            vm.timeline_spent_pct,
            vm.timeline_committed_pct,
            vm.timeline_fuzzy_left_pct,
            vm.timeline_fuzzy_width_pct,
            vm.today_pct,
        )
        today = datetime.now().date()
        last_day = calendar.monthrange(today.year, today.month)[1]
        month_abbr = calendar.month_abbr[today.month]
        self._hero.timeline.set_endpoints(f"1 {month_abbr}", f"{last_day} {month_abbr}")
        self._stats.set_snapshot(vm, animate=animate)

    def set_upcoming(self, rows) -> None:
        self._upcoming.set_upcoming(list(rows))

    def set_recent(self, rows) -> None:
        self._recent.set_recent(list(rows))

    def set_categories(self, rows) -> None:
        self._cat.set_categories(list(rows))

    def set_alert(self, body_html: str, amount_str: str, visible: bool) -> None:
        self._alert.set_alert(body_html, amount_str, visible)

    # ── Layout ────────────────────────────────────────────────────────────

    def _build_layout(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(self._build_content())
        outer.addWidget(scroll, stretch=1)

    def _build_content(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(tokens.CONTENT_PAD, 18, tokens.CONTENT_PAD, 18)
        v.setSpacing(14)

        # Alert banner (hidden by default)
        v.addWidget(self._alert)

        # Hero row: hero card + stat column
        hero_row = QWidget()
        hl = QHBoxLayout(hero_row)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(12)
        hl.addWidget(self._hero, stretch=1)
        hl.addWidget(self._stats)
        v.addWidget(hero_row)

        # 3-panel row
        panels = QWidget()
        pl = QHBoxLayout(panels)
        pl.setContentsMargins(0, 0, 0, 0)
        pl.setSpacing(10)
        pl.addWidget(self._cat,      stretch=1)
        pl.addWidget(self._upcoming, stretch=1)
        pl.addWidget(self._recent,   stretch=1)
        v.addWidget(panels)

        # Footer
        footer_div = QFrame()
        footer_div.setFixedHeight(1)
        footer_div.setStyleSheet(f"background: {tokens.HAIRLINE};")
        v.addWidget(footer_div)

        footer = QWidget()
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(0, 12, 0, 4)
        for text in ["MIZĀN · GUI V2", "STUDENT BUDGET TRACKER", ""]:
            lbl = QLabel(text)
            lbl.setObjectName("footerText")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fl.addWidget(lbl, stretch=1)
        v.addWidget(footer)

        return w
```

- [ ] **Step 5: Run the app to verify dashboard layout**

```bash
python -m expense_tracker.app.gui.main
```

Expected: Dashboard shows hero card (with gradient), stat column of 4 cards, 3 panels side by side, footer. All with placeholder "₪0" values.

- [ ] **Step 6: Commit**

```bash
git add src/expense_tracker/app/gui_v2/views/dashboard_page.py \
        src/expense_tracker/app/gui_v2/view_models/ \
        tests/unit/gui_v2/
git commit -m "feat(gui_v2): DashboardPage layout + BalanceViewModel with tests"
```

---

## Task 11: DashboardController + live data

**Files:**
- Create: `src/expense_tracker/app/gui_v2/controllers/__init__.py`
- Create: `src/expense_tracker/app/gui_v2/controllers/dashboard_controller.py`

- [ ] **Step 1: Copy and adapt DashboardController**

```bash
mkdir -p src/expense_tracker/app/gui_v2/controllers
touch src/expense_tracker/app/gui_v2/controllers/__init__.py
cp src/expense_tracker/app/gui/controllers/dashboard_controller.py \
   src/expense_tracker/app/gui_v2/controllers/dashboard_controller.py
```

- [ ] **Step 2: Update imports in the copied controller**

Open `src/expense_tracker/app/gui_v2/controllers/dashboard_controller.py` and change all imports from `gui.` to `gui_v2.`:

```python
# Replace this block at the top of the file:
from expense_tracker.app.gui.view_models.balance_view_model import BalanceViewModel

# With:
from expense_tracker.app.gui_v2.view_models.balance_view_model import BalanceViewModel
```

Also update the TYPE_CHECKING import:

```python
# Replace:
from expense_tracker.app.gui.views.main_window import MainWindow

# With:
from expense_tracker.app.gui_v2.views.main_window import MainWindow
```

- [ ] **Step 3: Wire controller row view models in the controller**

The existing controller's `_build_charge_rows`, `_build_tx_rows`, and `_build_category_rows` methods return dataclasses from `gui/widgets/panels.py`. Update them to return `gui_v2` panel view models instead:

Find the imports at the top that reference `gui/widgets/panels.py`:

```python
# Replace any import like:
from expense_tracker.app.gui.widgets.panels import ChargeRowVM, TxRowVM, CategoryRowVM

# With:
from expense_tracker.app.gui_v2.widgets.panels import ChargeRowVM, TxRowVM, CategoryRowVM
```

- [ ] **Step 4: Run the app with real data**

```bash
python -m expense_tracker.app.gui.main
```

Expected: Dashboard loads with real data from `data/charges.json`. Adding income/spend/charge via the "+" buttons (which are wired in MainWindow) opens dialogs. After adding, dashboard refreshes and numbers update with CountingLabel animation.

- [ ] **Step 5: Commit**

```bash
git add src/expense_tracker/app/gui_v2/controllers/
git commit -m "feat(gui_v2): DashboardController wired to real services"
```

---

## Task 12: Add Dialogs and Onboarding

**Files:**
- Create: `src/expense_tracker/app/gui_v2/dialogs/__init__.py`
- Create: `src/expense_tracker/app/gui_v2/dialogs/onboarding_dialog.py`
- Create: `src/expense_tracker/app/gui_v2/dialogs/add_income_dialog.py`
- Create: `src/expense_tracker/app/gui_v2/dialogs/add_spend_dialog.py`
- Create: `src/expense_tracker/app/gui_v2/dialogs/add_charge_dialog.py`

- [ ] **Step 1: Copy and clean onboarding dialog**

```bash
mkdir -p src/expense_tracker/app/gui_v2/dialogs
touch src/expense_tracker/app/gui_v2/dialogs/__init__.py
cp src/expense_tracker/app/gui/dialogs/onboarding_dialog.py \
   src/expense_tracker/app/gui_v2/dialogs/onboarding_dialog.py
cp src/expense_tracker/app/gui/dialogs/add_income_dialog.py \
   src/expense_tracker/app/gui_v2/dialogs/add_income_dialog.py
cp src/expense_tracker/app/gui/dialogs/add_spend_dialog.py \
   src/expense_tracker/app/gui_v2/dialogs/add_spend_dialog.py
cp src/expense_tracker/app/gui/dialogs/add_charge_dialog.py \
   src/expense_tracker/app/gui_v2/dialogs/add_charge_dialog.py
```

- [ ] **Step 2: Strip inline setStyleSheet from all copied dialogs**

For each dialog file, remove every `.setStyleSheet(...)` call. The global stylesheet applies automatically. After removing, add `self.setObjectName("dialog_name")` to each dialog's `__init__` so QSS rules can target them.

Pattern to remove (example from onboarding_dialog.py):
```python
# REMOVE lines like these:
self.setStyleSheet("background: white; ...")
some_widget.setStyleSheet("color: #abc; ...")
```

Pattern to add at the start of each dialog's `__init__`:
```python
self.setObjectName("onboardingDialog")  # or "addIncomeDialog" etc.
```

- [ ] **Step 3: Run the app — first-run onboarding**

Delete or rename `data/session.json` temporarily to trigger first-run:

```bash
mv data/session.json data/session.json.bak
python -m expense_tracker.app.gui.main
```

Expected: Onboarding dialog opens with the new stylesheet applied (navy button with gold text). Entering an opening balance and clicking confirm creates a session and opens the main window.

Restore:
```bash
mv data/session.json.bak data/session.json
```

- [ ] **Step 4: Run full smoke test**

```bash
python -m expense_tracker.app.gui.main
```

Verify:
- [ ] Dashboard loads with real data
- [ ] "+ Income" button opens add income dialog
- [ ] "+ Spend" button opens add spend dialog
- [ ] "+ Charge" button opens add charge dialog
- [ ] Adding an item refreshes the dashboard
- [ ] `USE_GUI_V2 = False` in `gui/main.py` launches the old GUI
- [ ] All existing unit tests still pass: `pytest tests/unit/ -v`

- [ ] **Step 5: Commit**

```bash
git add src/expense_tracker/app/gui_v2/dialogs/
git commit -m "feat(gui_v2): Phase 1-5 complete — Dashboard live with real data"
```

---

## Phase 1–5 Complete ✓

At this point `gui_v2` delivers:
- Full working Dashboard connected to real services
- Sidebar navigation, topbar with pulse pill
- HeroCard with correct gradient, states, and timeline
- 3 panels with live charge/transaction/category data
- Add income/spend/charge dialogs
- Onboarding flow for first run
- `USE_GUI_V2 = False` restores the old GUI instantly

---

## Next: Plan 2 — Remaining Pages + Polish (Phases 6–7)

Plan 2 covers:
- **Task A:** Activity page + LedgerViewModel + ActivityController
- **Task B:** Insights page + custom bar chart widgets + InsightsController
- **Task C:** Settings page + SettingsController (caution threshold, reduce-motion toggle)
- **Task D:** Toast widget
- **Task E:** Hover animations (QPropertyAnimation on interactive widgets)
- **Task F:** Streak box real data, bell notification dot
- **Task G:** Keyboard shortcuts verification + reduced-motion QSettings toggle

Write Plan 2 after Phase 1–5 is verified working.
