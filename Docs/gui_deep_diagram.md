# GUI Deep Diagram — Mizān Desktop Dashboard

This document explains the `src/expense_tracker/app/gui/` directory in **runtime order**, then breaks down how data flows through the GUI.

## 1. Runtime order

### Launch chain
1. `src/expense_tracker/app/gui/main.py`
2. `src/expense_tracker/app/gui/styles/fonts.py`
3. `src/expense_tracker/app/gui/styles/tokens.py`
4. `src/expense_tracker/app/gui/styles/textures.py`
5. `src/expense_tracker/app/gui/view_models/balance_view_model.py`
6. `src/expense_tracker/app/gui/controllers/dashboard_controller.py`
7. `src/expense_tracker/app/gui/views/main_window.py`
8. `src/expense_tracker/app/gui/widgets/sidebar.py`
9. `src/expense_tracker/app/gui/widgets/topbar.py`
10. `src/expense_tracker/app/gui/widgets/hero_card.py`
11. `src/expense_tracker/app/gui/widgets/timeline_widget.py`
12. `src/expense_tracker/app/gui/widgets/stat_column.py`
13. `src/expense_tracker/app/gui/widgets/panels.py`
14. `src/expense_tracker/app/gui/widgets/footer_strip.py`
15. `src/expense_tracker/app/gui/dialogs/add_spend_dialog.py`
16. `src/expense_tracker/app/gui/dialogs/add_income_dialog.py`
17. `src/expense_tracker/app/gui/dialogs/add_charge_dialog.py`

### Support files
- `src/expense_tracker/app/gui/GUI_BUILD_PLAN.md`
- `src/expense_tracker/app/gui/STAGE2_PYQT6_PLAN.md`

---

## 2. Top-level runtime flow

```text
python -m expense_tracker.app.gui.main
        ↓
QApplication starts
        ↓
Fonts load
        ↓
JSON repositories are created
        ↓
application services are created
        ↓
MainWindow is created
        ↓
DashboardController is created and connected
        ↓
controller.refresh()
        ↓
controller asks services for data
        ↓
controller builds BalanceViewModel
        ↓
MainWindow receives the view model
        ↓
widgets render the dashboard
```

---

## 3. Data flow diagram

```text
[Domain / Services]
   │
   │  BalanceService.aggregate_and_build_snapshot(...)
   │  SessionService.get_active()
   │  IncomeService / ChargeService / SpendService
   ▼
[DashboardController]
   │
   │  converts domain data into:
   │  BalanceViewModel
   │  + formatted money strings
   │  + percentage values
   │  + state strings
   ▼
[MainWindow.set_snapshot(view_model)]
   │
   ├── HeroCard.set_money(...)
   ├── HeroCard.set_state(...)
   ├── HeroCard.timeline.set_percentages(...)
   ├── Topbar.set_on_track_state(...)
   ├── StatColumn.set_snapshot(...)
   ├── set_upcoming(...)
   ├── set_recent(...)
   └── set_categories(...)
```

### Core rule
The GUI does **not** calculate free money, balance state, or timeline math. That work happens before the data reaches the widgets.

---

## 4. File-by-file breakdown

## `main.py`

### Responsibility
Bootstraps the GUI application.

### What it does
- fixes `sys.path`
- creates `QApplication`
- loads fonts
- creates repositories
- creates services
- creates `MainWindow`
- creates `DashboardController`
- calls `controller.refresh()`
- shows the window

### Why it matters
This is the start of the GUI runtime chain.

---

## `styles/fonts.py`

### Responsibility
Loads the bundled fonts into Qt.

### What it provides
- `load_fonts()`
- `playfair()`
- `dm_mono()`
- `naskh()`

### Why it matters
The dashboard mockup depends heavily on typography.

---

## `styles/tokens.py`

### Responsibility
Single source of truth for UI colors, spacing, and type sizes.

### What it contains
- colors like `BG`, `SURFACE`, `FG`, `GOLD`, `RED`, `GREEN`
- layout sizes like `SIDEBAR_W`, `STAT_COL_W`, `CONTENT_PAD`
- typography sizes like `T_MINI`, `T_SM`, `T_MD`

### Why it matters
Widgets should not hardcode design values.

---

## `styles/textures.py`

### Responsibility
Creates the dot-grain texture used in the background and hero card.

### Why it matters
It helps the UI match the HTML design mockup.

---

## `view_models/balance_view_model.py`

### Responsibility
Defines the UI-shaped data contract for balance display.

### Contains
- raw Decimal values
- formatted currency strings
- state strings
- timeline percentages
- supporting lists for event positions

### Why it matters
The view should only receive presentation-ready data.

---

## `controllers/dashboard_controller.py`

### Responsibility
The orchestrator between view and services.

### Main duties
- listen to signals from `MainWindow`
- call application services
- fetch a balance snapshot
- convert snapshot into `BalanceViewModel`
- push data back into the view

### Why it matters
This is the bridge between business data and presentation.

---

## `views/main_window.py`

### Responsibility
Builds the main dashboard shell.

### It creates
- `Sidebar`
- `Topbar`
- `HeroCard`
- `StatColumn`
- `CategoryPanel`
- `UpcomingPanel`
- `RecentPanel`
- `FooterStrip`

### Public setters
- `set_snapshot()`
- `set_upcoming()`
- `set_recent()`
- `set_categories()`
- `update_timeline()`
- `set_last_sync()`
- `set_alert()`

### Why it matters
It routes data to the child widgets, but does not compute business logic.

---

## 5. Widget breakdown

## `widgets/sidebar.py`

### What it shows
- brand block
- navigation items
- streak indicator
- user footer

### Signal
- `nav_changed(str)`

### Role
Presentation-only navigation column.

---

## `widgets/topbar.py`

### What it shows
- breadcrumb/date
- sparkline
- period selector
- status pill
- sync button
- bell button

### Signals
- `refresh_requested`
- `period_changed(str)`

### Role
Top status and control strip.

---

## `widgets/hero_card.py`

### What it shows
- free money title
- Mizān label
- period indicator
- big money value
- state badge
- legend row
- timeline widget
- inline alert row

### Public API
- `set_state()`
- `set_money()`
- `set_period()`
- `set_period_for_today()`
- `set_legend(...)`
- `set_today_changes(...)`
- `set_alert(...)`

### Role
This is the main center panel of the dashboard.

---

## `widgets/timeline_widget.py`

### What it shows
- calendar track
- spend day dots
- committed due-date dots
- today marker
- budget bar with committed, fuzzy, and spent segments

### Public API
- `set_percentages(...)`
- `set_committed_due_pcts(...)`
- `set_spend_day_pcts(...)`
- `set_endpoints(...)`

### Role
It paints timeline data, but does not calculate it.

---

## `widgets/stat_column.py`

### What it shows
- spent card
- committed card
- monthly left card
- burn bars

### Public API
- `set_snapshot(vm)`
- `set_delta(pct, direction)`
- `set_due_in(text)`

### Role
Shows the right-side summary metrics.

---

## `widgets/panels.py`

### What it contains
- `CategoryRowVM`
- `ChargeRowVM`
- `TxRowVM`
- `CategoryPanel`
- `UpcomingPanel`
- `RecentPanel`

### Role
Renders the bottom dashboard panels.

---

## `widgets/footer_strip.py`

### What it shows
- left footer label
- center footer label
- right footer label

### Role
Simple footer summary row.

---

## `widgets/heads_up_alert.py`

### What it is
An amber alert strip widget.

### Note
This looks like an alternate or legacy alert implementation, because `HeroCard` also has its own inline alert row.

---

## 6. Dialog flow

### `dialogs/add_spend_dialog.py`
Collects:
- amount
- description
- category
- date

### `dialogs/add_income_dialog.py`
Collects:
- amount
- source tag
- date

### `dialogs/add_charge_dialog.py`
Collects:
- charge name
- amount
- due date
- recurring flag
- day of month
- reminder lead time

### Purpose
Dialogs gather raw user input and hand it back to the controller.

---

## 7. User-action loop

```text
User clicks a button in the UI
        ↓
MainWindow emits a signal
        ↓
DashboardController receives the signal
        ↓
Controller opens dialog
        ↓
User fills dialog and accepts
        ↓
Controller calls matching application service
        ↓
Service validates and writes through repository
        ↓
Controller calls refresh()
        ↓
MainWindow updates all display widgets
```

### Examples

#### Add income
```text
Click "Add Income"
  → MainWindow.add_income_requested
  → DashboardController._on_add_income_requested()
  → AddIncomeDialog
  → IncomeService.add_income(...)
  → refresh()
```

#### Add spend
```text
Click "Add Spend"
  → MainWindow.add_spend_requested
  → DashboardController._on_add_spend_requested()
  → AddSpendDialog
  → SpendService.add_transaction(...)
  → refresh()
```

#### Add charge
```text
Click "Add Charge"
  → MainWindow.add_charge_requested
  → DashboardController._on_add_charge_requested()
  → AddChargeDialog
  → ChargeService.add_charge(...) or add_recurring_charge(...)
  → refresh()
```

---

## 8. Dependency direction

```text
GUI views/widgets/dialogs
        ↓
GUI controllers/view models
        ↓
Application services
        ↓
Ports / repository interfaces
        ↓
Infrastructure JSON repositories
```

### Forbidden reverse directions
- widgets should not call repositories
- widgets should not call services directly
- services should not depend on Qt
- domain should not import GUI
- GUI should not calculate business totals

---

## 9. Presentation-only rule

### Allowed in GUI
- display data
- gather input
- show dialogs
- emit signals
- format text for display
- redraw widgets

### Not allowed in GUI
- calculate free money
- decide balance state
- write JSON files
- bypass validators
- access repositories directly

---

## 10. Summary

The GUI directory is organized as a layered presentation system:

- `main.py` starts the app
- `DashboardController` coordinates services and view models
- `MainWindow` composes the screen
- widgets render the visual pieces
- dialogs collect input
- styles hold the design system

The strongest design rule is simple:

> **The GUI renders; services decide.**

