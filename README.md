# Mizān — Student Expense Tracker

A PyQt6 desktop budgeting app built for Israeli university students. Mizān (ميزان / מאזן, "balance") tracks one number: **how much money you can actually spend today**, after your committed obligations are subtracted.

---

## Core concept

```
free money = opening balance − committed charges − recorded spends
```

Every item in the app maps to this formula:

| Concept | What it is |
|---|---|
| **Session** | A financial period starting with your opening balance |
| **Committed charge** | A fixed upcoming bill (rent, subscriptions, tuition) |
| **Recurring charge** | A monthly bill that auto-schedules the next occurrence on payment |
| **Fuzzy charge** | An uncertain future expense (estimated, resolved when the real bill arrives) |
| **Spend** | A recorded transaction that reduces your free money immediately |
| **Free money** | What's left — the live number on the dashboard |

---

## Screenshots

> _Add a screenshot or GIF here once the app is running with demo data._
> `mizaan --demo` (coming soon) will seed a session so the dashboard is never empty for first-run.

---

## Quick start

**Requirements:** Python 3.10+, PyQt6

```bash
git clone https://github.com/moamin/student-expense-tracker.git
cd student-expense-tracker
pip install -e .
mizaan
```

Or run directly without installing:

```bash
pip install PyQt6
python -m expense_tracker.app.gui.main
```

---

## Project structure

```
src/expense_tracker/
├── domain/          # Pure models and validators — no I/O
├── application/     # Services: ChargeService, SpendService, BalanceService …
├── infrastructure/  # JSON persistence with atomic writes and mtime-keyed cache
└── app/
    ├── gui/         # PyQt6 views, controllers, and design tokens
    └── cli/         # Minimal CLI entry point
tests/unit/          # 260+ unit tests, no mocks on persistence layer
```

The architecture follows a ports-and-adapters pattern: services depend on repository interfaces, the JSON layer implements those interfaces, and the GUI layer depends only on services. Swapping the storage backend requires no changes outside `infrastructure/`.

---

## Running tests

```bash
pip install -e ".[dev]"
pytest
```

The test suite hits real JSON files via `tmp_path` fixtures — no in-memory mocks — so every repository round-trip is covered.

---

## Design notes

- **Light theme** is the default. The warm cream palette (`#FAF7F2`) is the native design; dark mode is a deferred refactor.
- **Free money is session-scoped**, not monthly. Salary and opening balance carry forward; monthly budgeting layers on top via the Insights page.
- **Atomic writes** — every JSON save goes through a temp-file rename so a crash never corrupts live data. A `.bak` sidecar is kept for recovery. Data files are created `0600` (owner-readable only).
- **No external database** — the app is self-contained; all data lives under `data/` in the project root.

---

## License

MIT — see [LICENSE](LICENSE) if present, or treat as open-source.
