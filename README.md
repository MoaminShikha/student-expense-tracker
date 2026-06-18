# Mizān — Student Expense Tracker

A web-based budgeting app for students. Mizān (ميزان / מאזן, "balance") tracks one number: **how much money you can actually spend today**, after committed obligations are subtracted.

```
free money = opening balance − committed charges − recorded spends
```

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS |
| Backend | FastAPI (Python 3.10+) |
| Storage | JSON files under `data/` (no database required) |

---

## Quick start

**Requirements:** Python 3.10+, Node.js 18+

```bash
git clone https://github.com/MoaminShikha/student-expense-tracker.git
cd student-expense-tracker

# Backend
pip install -e .
start-backend.bat        # Windows
# or: PYTHONPATH=src python -m uvicorn expense_tracker.app.api:app --host 127.0.0.1 --port 8000

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```

Open **http://localhost:5173** (or whichever port Vite picks).

---

## Features

| Feature | Description |
|---|---|
| Dashboard | Live balance, month timeline with event dots, stats row |
| Activity | Full transaction history, search, filter, CSV export |
| Insights | Weekly spend chart, category breakdown, smart nudges |
| Settings | Currency symbol/code (stored in browser localStorage) |
| Charges | Committed upcoming bills tracked separately from spend |

---

## Project structure

```
src/expense_tracker/
├── domain/          # Pure models — no I/O
├── application/     # Services: ChargeService, BalanceService, …
├── infrastructure/  # JSON persistence with atomic writes
└── app/
    ├── api.py       # FastAPI endpoints
    └── cli/         # CLI entry point

frontend/src/
├── components/      # UI components (dashboard, forms, layout, insights)
├── hooks/           # Data-fetching hooks (useFetch, useBalance, …)
├── pages/           # Dashboard, Activity, Insights, Settings
├── services/        # API client (api.ts)
└── types/           # Shared TypeScript interfaces

tests/unit/          # 260+ unit tests — real JSON files, no mocks
```

---

## Running tests

```bash
pip install -e ".[dev]"
pytest
```

---

## Configuration

| Environment variable | Default | Description |
|---|---|---|
| `MIZAN_CORS_ORIGINS` | `http://localhost:5173,...` | Comma-separated allowed origins |

---

## Design notes

- **One session at a time** — open a session with your opening balance; it persists until you reset.
- **Atomic writes** — every JSON save goes through a temp-file rename. A `.bak` sidecar is kept for crash recovery.
- **No external database** — all data lives under `data/` (git-ignored).
- **localStorage settings** — currency symbol/code and display name are stored in the browser.

---

## License

MIT
