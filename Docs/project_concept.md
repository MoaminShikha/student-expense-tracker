# Student Cash-Flow Visibility Tool — Project Concept

> This document tracks the idea as it develops. Updated incrementally as decisions are made.

---

## The Problem

Students run out of money without seeing it coming.

Their bank balance includes money already committed to upcoming charges — rent due next week, a tuition instalment, a phone bill. Nothing tells them what's actually safe to spend today. The result is a cycle most students know well: the balance looks fine, spending continues normally, then a charge hits and the account is suddenly empty.

This is not a willpower problem. It is a visibility problem.

### Supporting Evidence

| Source | Finding |
|---|---|
| [Edvisors survey — Money.com](https://money.com/college-students-running-out-of-money/) | 64% of college students run out of money before the end of the semester |
| [Save the Student — National Student Money Survey 2025](https://www.savethestudent.org/money/surveys/student-money-survey-2025-results.html) | 80% of students worry about making ends meet; average monthly shortfall is £502 |
| [Bankrate — Available vs Current Balance](https://www.bankrate.com/banking/checking/what-is-your-available-balance/) | Bank balance ≠ spendable money — committed pending charges are not deducted |
| [Israeli State Comptroller — Cost of Living Report](https://www.mevaker.gov.il/en/media/magazine/cost-of-living) | Israeli households face NIS 8,000–12,000 in unexpected additional annual costs in 2025 |
| [Times of Israel — Food Prices Jan 2026](https://www.timesofisrael.com/israelis-hit-by-soaring-food-prices-as-producers-grocers-feast-on-wartime-windfall/) | Food prices in Israel are 51% above EU averages; cost of living ranks as top national concern |
| [Israel Hayom — Student Budgeting Guide Feb 2025](https://www.israelhayom.com/2025/02/03/student-budgeting-in-israel-a-survival-guide-for-smart-spenders/) | Israeli students face "high tuition fees, rising living expenses, and the need to balance studies with work" |

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
The home screen shows a progress bar: how much of this month's budget has been spent, and whether spending is on track. Monthly budget is calculated as income expected this month minus committed charges due this month. The on-track signal is percentage-based — green below 100%, yellow at 100–110%, red above 130%. Thresholds are app-suggested and student-overridable. If free money falls to zero or below, the balance area turns red and shows the actual negative number — the app never hides reality.

### 2. Committed vs free money separation
The engine of the app. All logged income is immediately split. Upcoming charges are deducted from free money the moment they are entered — not when they hit the bank. The student always knows what is truly available, not what looks available.

### 3. Upcoming payment log with pre-charge reminders
The student enters known recurring and one-off charges once. Rent on the 1st. Tuition instalment on the 15th. Phone bill on the 22nd. The app deducts them from free money immediately and surfaces a quiet reminder before each charge lands. When a recurring charge is marked as paid, the next occurrence is created immediately and deducts from free money at that moment — the student is notified, not asked to confirm. Each charge carries its own reminder lead time (default 3 days, student-overridable).

Crucially, the student can also log a **fuzzy charge** — a payment they know is coming on a specific date but whose exact amount is not yet known (e.g. a variable electricity bill, an unconfirmed tuition adjustment). The app flags the date with a reminder alert without deducting an amount, prompting the student to confirm the charge when it arrives.

### 4. Automatic spend pattern awareness
After enough data accumulates, the app surfaces one observation about where money is actually going versus where the student thinks it is going. Not a lecture. Not a list of tips. One plain sentence, once, when the data earns it: *"You've spent ₪400 on food delivery this month — 60% of your food budget — and it's only the 18th."*


---

## Key Design Decisions (from weakness resolutions)

### Balance state system
Free money has three states: **normal** (above threshold), **caution** (yellow — at or below student-set threshold, default 7 × average daily spend), **crisis** (red — at or below ₪0). The daily number shows ₪0 in crisis. The actual negative amount is always shown. The red/yellow colour applies to the balance area only — no modal, no dismiss button, persists until free money returns to positive. In crisis, a full ranked spending breakdown by category is surfaced automatically.

### Occurrences screen
A dedicated screen listing all events waiting for student action — primarily unresolved fuzzy charges. Fuzzy charges have three states: pending, overdue (gray, past due date but unresolved), and resolved/discarded. Tapping a notification shows Confirm / Delete / ✕ (dismiss without deciding). No auto-discard ever.

### Pattern detection gate
PatternDetector will not fire until BOTH conditions are met: at least 14 calendar days have passed since first transaction AND at least 20 transactions have been logged. Spike threshold is 50% above rolling monthly average — a conservative default to be adjusted empirically in Stage 4. False negatives always preferred over false positives.

### New data entities from resolutions
- **BalanceThreshold** — stores the student caution threshold. App-suggested, student-overridable.
- **FuzzyChargeLog** — separate store for date-only charges. Never touches BalanceEngine.
- **AppSession** — replaces AcademicYearContext. Fields: start_date, opening_balance, optional period_name. No end date.

---

## What This Is Not (Scope Boundaries)

- Not a full accounting system
- Not a bank integration (for now — local bank connectivity is a very late stage consideration)
- Not an investment or savings product
- Not a pie chart dashboard
- App runs continuously — no forced period reset. Student can optionally start a named period.
- Monthly budgeting unit — not daily, not academic year
- No manual savings tip lists — automatic surface only
- Pattern detection requires 14 days AND 20 transactions before firing — no premature insights

---

## Fintech Category

**Primary:** Personal Finance Management (PFM)
**Niche:** Student cash-flow planning — committed vs free money

**Adjacent fintech concepts demonstrated:**
- Cash-flow forecasting (projecting runway from known outflows + burn rate)
- Committed vs available funds (core treasury management concept, applied personally)
- Behavioural nudges (one relevant insight at the right moment)
- Multi-source income reconciliation (scholarships + family + work → one number)

---

## Origin

Built because the builder had the problem personally.

*"I never know how long money will last — and I find myself with no money, not knowing which college or living charge hit me, or where it went."*

That is the problem statement. The app is the answer.


---

## Build Stages

**Bottom line:** Put the data model in early, reminders before reporting, reporting before intelligence, and web UI only after the logic is already real.

### Stage 1 — Core session + full charge model
- Session setup (AppSession — opening balance, start date)
- Income logging with source tags
- Charge logging — one-off and committed
- Recurring charges
- Fuzzy charges (date known, amount unknown)
- Spend logging with optional category
- Free money calculation
- Monthly safe-to-spend number and on-track signal

*Delivers: a complete CLI tool a real student could use daily.*

### Stage 2 — Persistence
- Save and reload everything across restarts
- Move from CSV/JSON to SQLite
- Stable local storage — FuzzyChargeLog as its own table
- No feature logic changes

*Delivers: nothing lost between sessions.*

### Stage 3 — Reminders
- Upcoming charge reminders (T-3 days)
- Fuzzy charge date alerts and follow-up prompts
- Auto-generation of next recurring charge on mark-as-paid
- Occurrences screen — all unresolved items in one place

*Delivers: the core promise — notified before a charge hits, not after.*

### Stage 4 — Summaries and history
- Monthly totals and spend breakdowns
- History view — all calendar months since first use
- Activity views — recent transactions, what's been spent vs what's left
- Three-state balance display (normal / caution / crisis)
- Crisis ranked spending breakdown

*Delivers: a complete, fully-functional CLI product.*

### Stage 5 — Insights
- Pattern detection with hard gates (14 days AND 20 transactions)
- One surfaced observation per category per calendar month
- Threshold rules and insight persistence
- False negative preference — no premature insights

*Delivers: the app notices things the student hasn't noticed.*

### Stage 6 — Web UI
- Move from CLI to browser interface
- FastAPI backend wrapping existing logic — unchanged
- Streamlit frontend: progress bar, monthly number, Occurrences, history
- CLI continues to work independently

*Delivers: the shareable portfolio piece.*

### Stage 7 — Advanced integrations
- Local bank connectivity (read-only OFX/CSV import)
- Multi-currency support (NIS + USD/EUR via exchange rate API)
- Natural language transaction entry
- Other optional expansions — added only if they solve a real problem

*Delivers: production-grade. Optional, additive, never breaking.*

---

## Status

- [x] Problem identified and article-backed
- [x] User defined
- [x] Core mechanic decided
- [x] Four pillars locked
- [x] Scope boundaries set
- [x] All six design weaknesses resolved
- [x] Build stages defined (7 stages)
- [ ] Feature list (Stage 1)
- [ ] Data model (Stage 1)
- [ ] Tech stack decision
- [ ] Build

---

*Last updated: April 2026 — v1.4: build stages locked (7 stages), data model before reporting before intelligence before UI*
