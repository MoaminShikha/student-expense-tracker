# Student Cash-Flow Visibility Tool — Project Concept

> This document tracks the idea as it develops. Updated incrementally as decisions are made.

---

## The Problem

Students run out of money without seeing it coming.

Their bank balance includes money already committed to upcoming charges — rent due next week, a tuition instalment, a phone bill. Nothing tells them what's actually safe to spend today. The result is a cycle most students know well: the balance looks fine, spending continues normally, then a charge hits and the account is suddenly empty.

This is not a willpower problem. It is a visibility problem.

---

## The User

**An Israeli university student during the academic year.**

Specifically:
- Managing irregular income from multiple sources (family transfers, scholarships, part-time shifts)
- Sharing living costs with flatmates (rent, utilities, groceries)
- Doing financial planning via rough mental calculation — no app, no spreadsheet
- Unaware of upcoming charges until they hit — including charges with a known due date but unknown exact amount
- Wants to know one thing when they open an app: *am I on track this month?*

---

## The Core Idea

**Committed money vs free money.**

Your bank balance is not your spendable money. This app shows you the truth.

The moment income arrives, the app separates it into two buckets:

- **Committed money** — rent due in 8 days, tuition instalment next week, phone bill on the 22nd. Already spoken for. Removed from the display immediately.
- **Free money** — what is genuinely available to spend without consequence.

The number shown on the home screen is always the free money. Not the bank balance. Not the available balance. The free money after all known upcoming charges are accounted for.

---

## The Four Pillars

### 1. Monthly budget with on-track signal
The home screen shows a progress bar: how much of this month's budget has been spent, and whether spending is on track. Monthly budget is calculated as income expected this month minus committed charges due this month. The on-track signal is percentage-based — green below 100%, yellow at 100–130%, red above 130%. Thresholds are app-suggested and student-overridable. If free money falls to zero or below, the balance area turns red and shows the actual negative number — the app never hides reality.

### 2. Committed vs free money separation
The engine of the app. All logged income is immediately split. Upcoming charges are deducted from free money the moment they are entered — not when they hit the bank. The student always knows what is truly available, not what looks available.

### 3. Upcoming payment log with pre-charge reminders
The student enters known recurring and one-off charges once. Rent on the 1st. Tuition instalment on the 15th. Phone bill on the 22nd. The app deducts them from free money immediately and surfaces a quiet reminder before each charge lands. When a recurring charge is marked as paid, the next occurrence is created immediately and deducts from free money at that moment — the student is notified, not asked to confirm. Each charge carries its own reminder lead time (default 3 days, student-overridable).

The student can also log a **fuzzy charge** — a payment they know is coming on a specific date but whose exact amount is not yet known (e.g. a variable electricity bill, an unconfirmed tuition adjustment). The app flags the date with a reminder alert without deducting an amount, prompting the student to confirm the charge when it arrives.

### 4. Automatic spend pattern awareness
After enough data accumulates, the app surfaces one observation about where money is actually going versus where the student thinks it is going. Not a lecture. Not a list of tips. One plain sentence, once, when the data earns it: *"You've spent ₪400 on food delivery this month — 60% of your food budget — and it's only the 18th."*

---

## Key Design Decisions

### Balance state system
Free money has three states: **normal** (above threshold), **caution** (yellow — at or below student-set threshold, default 7 × average daily spend), **crisis** (red — at or below ₪0). The daily number shows ₪0 in crisis. The actual negative amount is always shown. The red/yellow colour applies to the balance area only — no modal, no dismiss button, persists until free money returns to positive. In crisis, a full ranked spending breakdown by category is surfaced automatically.

### Occurrences screen
A dedicated screen listing all events waiting for student action — primarily unresolved fuzzy charges. Fuzzy charges have three states: pending, overdue (gray, past due date but unresolved), and resolved/discarded. Tapping a notification shows Confirm / Delete / ✕ (dismiss without deciding). No auto-discard ever.

### Pattern detection gate
PatternDetector will not fire until BOTH conditions are met: at least 14 calendar days have passed since first transaction AND at least 20 transactions have been logged. Spike threshold is 50% above rolling monthly average — a conservative default to be adjusted empirically in Stage 4. False negatives always preferred over false positives.

### New data entities from resolutions
- **BalanceThreshold** — stores the student caution threshold. App-suggested, student-overridable.
- **FuzzyChargeLog** — separate store for date-only charges. Never touches BalanceEngine.
- **AppSession** — replaces AcademicYearContext. Fields: start_date and opening_balance. No end date.

---

## What This Is Not

- Not a full accounting system
- Not a bank integration (for now — local bank connectivity is a very late stage consideration)
- Not an investment or savings product
- Not a pie chart dashboard
- App runs continuously — no forced period reset. Student can optionally start a named period.
- Monthly budgeting unit — not daily, not academic year
- No manual savings tip lists — automatic surface only
- Pattern detection requires 14 days AND 20 transactions before firing — no premature insights
- No contextual discovery features yet (nearby stores, housing listings) — planned for a future stage beyond Stage 7

---

## Fintech Category

**Primary:** Personal Finance Management (PFM)
**Niche:** Student cash-flow planning — committed vs free money

**Adjacent fintech concepts demonstrated:**
- Cash-flow forecasting (projecting runway from known outflows + burn rate)
- Committed vs available funds (core treasury management concept, applied personally)
- Behavioural nudges (one relevant insight at the right moment)
- Multi-source income reconciliation (scholarships + family + work → one number)

*Full reference library and glossary in `references.md`.*

---

## Build Stages

**Bottom line:** Put the data model in early, reminders before reporting, reporting before intelligence, and web UI only after the logic is already real.

| Stage | Delivers |
|---|---|
| 1 — CLI + JSON | Complete CLI tool with all core logic, services, and JSON persistence tested |
| 2 — CustomTkinter Dashboard | Real app feel — opens to a dashboard, usable without terminal commands |
| 3 — PostgreSQL Persistence | Nothing lost between sessions, production-grade storage |
| 4 — Reminders + Pattern Detection | Notified before a charge hits; app notices things the student hasn't noticed |
| 5 — Web UI | Shareable portfolio piece — FastAPI backend, React or Streamlit frontend |
| 6 — Advanced Integrations | Local bank connectivity, multi-currency, natural language entry |

---

## Future Vision

Features deliberately outside current scope — noted to prevent premature building.

**Contextual discovery:** If the student consistently overspends on groceries, the app could surface discount supermarkets near their campus (Rami Levy, Osher Ad). If rent is a dominant budget pressure, surface relevant housing listings nearby. If a student discount exists for a category they just logged — one sentence, once, at the right moment. Not a directory. Not a list.

Requires external data sources, location permissions, and Israeli-specific data partnerships. Not built until Stages 1–6 are stable.

---

## Origin

Built because the builder had the problem personally.

*"I never know how long money will last — and I find myself with no money, not knowing which college or living charge hit me, or where it went."*

That is the problem statement. The app is the answer.

---

## Status

- [x] Problem identified and article-backed
- [x] User defined
- [x] Core mechanic decided
- [x] Four pillars locked
- [x] Scope boundaries set
- [x] All six design weaknesses resolved
- [x] Build stages defined
- [x] Stage 1 complete — 208/208 tests passing

---

*Last updated: April 2026*
