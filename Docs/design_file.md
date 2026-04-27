# Design File — Student Cash-Flow Visibility Tool

> Built following the xperience.works methodology: Building a Design File from Scratch with an AI Partner.
> This is a first complete design draft, ready for deeper review later.
> Uncertainty, tradeoffs, and open questions are preserved deliberately — not smoothed over.

---

## Step 1 — Setup

**Working rules for this session:**
- No invented facts
- Facts, assumptions, and open questions kept strictly separate
- Design stays high-level and no-code unless explicitly requested
- Incremental — no section jumps ahead of its foundations
- No premature architecture

---

## Step 2 — Raw Feature Brief *(working note only — not copied to design file)*

What it is: An academic-year-first budget tracker for Israeli university students that separates committed money from free money and tells the student one honest number — what they can safely spend today.

Who needs it: Israeli university students during the academic year, managing irregular income from multiple sources (family transfers, scholarships, part-time shifts), sharing living costs, and doing financial planning via rough mental calculation.

Why it exists: Students consistently run out of money before the academic year ends without seeing it coming. Their bank balance includes money already spoken for — upcoming rent, tuition instalments, subscriptions — but nothing deducts these future charges until they actually hit. The result is a false sense of available funds and a sudden, avoidable shortfall.

What system areas it touches: income logging, upcoming charge tracking, daily budget calculation, spend logging, pattern detection, notification/reminder system.

What we already know:
- Core mechanic is committed vs free money
- Home screen shows one number: today's safe-to-spend amount
- Upcoming payment log with pre-charge reminders
- Automatic spend pattern awareness (one insight, surfaced once, when data earns it)
- Academic year-scoped only — no break mode for now
- No bank API integration at this stage
- No chatbot — arithmetic is the intelligence

What we are unsure about:
- Exact data model structure
- How pattern detection thresholds are set
- Whether multi-currency (NIS + USD/EUR) is in scope for Stage 1
- How roommate cost-splitting is handled if at all in Stage 1
- Notification mechanism (in-app only vs push)

---

## Problem Statement

Students running out of money before the academic year ends is not a willpower problem — it is a visibility problem. A student's bank balance includes money already committed to upcoming charges (rent due next week, a tuition instalment, a phone bill), but nothing deducts these future obligations until they physically clear. The student sees a balance that looks available, spends against it, and only discovers the shortfall when a charge lands and the account is suddenly empty. No mainstream budgeting tool solves this for the specific financial structure of a university student — academic year-based income, multiple irregular sources, and a mix of fixed recurring and one-off charges hitting at different times.

**Success conditions:**
1. A student can open the app and immediately see how much they can safely spend today
2. The displayed number accounts for all known upcoming charges, not just the current bank balance
3. The student is notified before a committed charge lands — not after
4. After sufficient data, the app surfaces one spend pattern observation without requiring the student to ask
5. A student who uses the app for a full academic year does not run out of money due to a charge they forgot about
6. The app requires no financial expertise to set up or use daily

---

## Goals

- Show a single honest safe-to-spend number derived from free money (income minus all committed upcoming charges) using the active period rule
- Separate committed money from free money as the core financial mechanic
- Allow students to log income from multiple sources (family, scholarship, part-time work) with source tags
- Allow students to log upcoming charges as either recurring or one-off, with a due date
- Remind students 3 days before a committed charge lands
- Detect and surface one spend pattern observation automatically when the data justifies it
- Keep period-aware budgeting clear while allowing continuous use across multiple periods
- Be usable by someone with no financial background in under 5 minutes of setup

## Non-Goals

- No bank or payment API integration in this version (local bank connectivity reserved for Stage 6)
- No break mode or holiday automation in Stage 1
- No investment, savings, or wealth-building features
- No manual savings tip lists or generic financial advice
- No roommate cost-splitting feature in Stage 1
- No multi-currency support in Stage 1
- No social or sharing features
- No chatbot or conversational interface in Stage 1
- Not designed for non-students or post-graduation financial management
- Not a full accounting or bookkeeping system

---

## Context and Constraints

### Technical
- Stage 1 is a CLI tool with JSON storage — no web framework yet
- Stage 2 replaces the CLI with a **CustomTkinter desktop GUI dashboard** — the app opens directly to a live dashboard window; all input happens via buttons and modal forms; JSON storage remains
- Stage 3 introduces PostgreSQL as the persistence layer — JSON adapters are swapped; domain and service layers are untouched
- Stage 4 introduces reminders and pattern detection on top of the existing app layers
- Stage 5 introduces FastAPI backend and a React or Streamlit web frontend
- No external API dependencies in Stages 1–3
- Pattern detection uses only the student's own logged data — no external benchmarks in Stage 1
- All calculation logic must be testable in isolation from the UI

### Product
- The primary user is a CS student building this as a portfolio project — they are also the target user
- The app runs continuously; students can optionally mark new periods without resetting the full app session
- The daily number is the product's core identity — no feature should obscure or compete with it
- Automatic insights must feel earned by data, not forced — if data is insufficient, no insight is surfaced
- The app must work without internet access for core functionality

### Operational
- Initially a personal tool — no multi-user, no accounts, no authentication in Stage 1
- Data lives locally — no cloud storage in Stage 1
- Stage 5 introduces a web dashboard, but the CustomTkinter dashboard must continue to work independently
- No deployment infrastructure needed until Stage 5

### Organizational
- Solo developer project
- Each stage must be independently demonstrable and usable
- Stages build on each other — Stage N+1 does not break Stage N
- The project doubles as a fintech portfolio piece — code quality, commit history, and README matter

---

## Facts, Assumptions, and Open Questions

### Confirmed Facts
- 64% of college students run out of money before the end of the academic year (Edvisors survey)
- 80%+ of students worry about making ends meet; average monthly shortfall is £502 (Save the Student 2025)
- Israeli food prices are 51% above EU averages (State Comptroller / OECD)
- Israeli households faced NIS 8,000–12,000 in unexpected additional annual costs in 2025 (State Comptroller)
- Bank balance ≠ spendable money — pending and upcoming charges are not deducted (Bankrate)
- The primary user manages income from 3–5 irregular sources simultaneously
- The primary user currently does financial planning via rough mental calculation only
- The primary user wants one number when opening the app: am I on track today?

### Assumptions
- Students may still think in academic-year periods, but period markers are optional rather than mandatory resets
- The student knows their major upcoming charges in advance (rent day, tuition date, phone bill)
- Income is logged manually — no automatic bank feed
- The student will log transactions manually, at least daily during active use
- Pattern detection becomes meaningful after approximately 2–3 weeks of data
- A daily safe-to-spend number is more useful than a weekly or monthly number for this user
- The student's budgeting model does not account for emergency expenses — this is a known limitation
- NIS is the primary currency for Stage 1

### Open Questions
- **How should optional period markers be suggested without forcing resets?** Matters because reminders should help planning without breaking continuous history.
- **What happens when income arrives mid-year and changes the daily number significantly?** Matters because a large mid-year family transfer could make the number look artificially safe.
- **How many days of data are needed before the pattern detection fires?** Matters because firing too early produces unreliable insights that erode trust.
- **Is the daily number recalculated in real time as transactions are logged, or once per day?** Matters for UX accuracy and implementation complexity.
- **What is the correct behaviour when free money goes negative?** Matters because this is the crisis state the app exists to prevent — the response should be distinct from normal warnings.
- **How should a fuzzy charge (known date, unknown amount) affect the daily number?** Matters because the student is aware of a financial obligation but cannot deduct it. The app must flag the date clearly without falsely inflating free money.

---

## Actors and Workflows

### Actors
- **Student (primary)** — sets up the app session, logs income, logs upcoming charges, logs daily transactions, reads the budget signal
- **The app (system)** — calculates free money, computes daily safe-to-spend, triggers reminders, detects spend patterns, surfaces insights

### Workflows

**Workflow 1 — Initial setup / optional period setup**
- Trigger: Student opens app for the first time, or chooses to mark a new planning period
- Steps: Enter opening balance → optionally set a period label and target end date → optionally pre-load known recurring charges (rent, phone bill, transport pass)
- State changes: App session exists; optional period metadata is saved; committed charges registered; free money calculated from opening balance minus all committed charges; first budget signal computed
- Dependencies: None — this is the root workflow

**Workflow 2 — Log income**
- Trigger: Student receives money (scholarship drop, family transfer, shift payment)
- Steps: Enter amount → tag source type (scholarship / family / work / other) → confirm date
- State changes: Free money increases; daily number recalculates; if increase is large, a contextual note may surface ("your daily budget has increased to ₪X")
- Dependencies: Active app session must exist

**Workflow 3 — Log upcoming charge**
- Trigger: Student remembers or discovers a future payment obligation
- Steps: Enter charge name → enter amount → enter due date → tag as recurring or one-off → if recurring, set frequency
- State changes: Committed money increases by charge amount immediately; free money decreases by same amount; daily number recalculates; reminder scheduled for 3 days before due date
- Dependencies: Active app session must exist

**Workflow 4 — Log daily transaction**
- Trigger: Student spends money
- Steps: Enter amount → enter description → optionally tag category (food / transport / entertainment / education / other)
- State changes: Free money decreases; today's spend accumulates; daily spend compared to daily safe-to-spend number; on-track status updates
- Dependencies: Active app session must exist; free money can be positive or negative, with state-aware display

**Workflow 5 — Pre-charge reminder**
- Trigger: System detects a committed charge is due in 3 days
- Steps: App surfaces reminder — charge name, amount, due date, confirmation that amount is already deducted from free money
- State changes: None — reminder is informational only; the charge was already deducted from free money at the time it was logged
- Dependencies: Upcoming charge must have been logged; reminder must not have fired already for this charge

**Workflow 5b — Fuzzy charge reminder**
- Trigger: Student logs a payment they know is coming on a specific date but whose exact amount is unknown (e.g. variable electricity bill, unconfirmed tuition adjustment)
- Steps: Enter charge name → enter due date → mark as amount-unknown → no amount deducted
- State changes: No deduction from free money; date-only reminder scheduled for 3 days before the due date
- Dependencies: Active app session must exist

**Workflow 6 — Spend pattern insight**
- Trigger: System detects that a spend category has exceeded its rolling average by a threshold, after sufficient data exists
- Steps: App surfaces one plain-language observation once — e.g. "You've spent ₪400 on food delivery this month — 60% of your food budget — and it's only the 18th"
- State changes: Insight marked as surfaced — will not repeat for this pattern in this period
- Dependencies: Minimum data threshold met (approx. 14 days of logged transactions); category spend exceeds threshold; insight has not already been surfaced for this category this period

**Workflow 7 — Daily number check (passive)**
- Trigger: Student opens the app
- Steps: App displays daily safe-to-spend number; today's spend so far; on-track / over indicator; next upcoming charge with days until it lands
- State changes: None — read-only display
- Dependencies: Active app session; at least one income source logged

---

## Invariants

**Invariant 1 — Free money is always non-negative in display**
- Statement: The app must never display a negative free money value as if it were normal
- Break scenario: Student logs more committed charges than available income
- Trigger: Total committed charges exceed total logged income
- Protection note: When committed charges would push free money below zero, the app must surface an explicit warning state — not silently show a negative number

**Invariant 2 — Budget signal is always derived from free money, never from bank balance**
- Statement: The displayed safe-to-spend/budget signal is always computed from free money with committed charges pre-deducted
- Break scenario: A code change accidentally uses total balance instead of free money in the calculation
- Trigger: Developer error or refactor that bypasses the committed charge deduction
- Protection note: Unit tests must assert this calculation explicitly with known inputs

**Invariant 3 — A committed charge is deducted from free money at log time, not at due date**
- Statement: The moment a charge is entered, it reduces free money — it does not wait until the due date
- Break scenario: Charge is stored but not deducted until it "clears"
- Trigger: Incorrect implementation treating upcoming charges like actual transactions
- Protection note: This is the core mechanic — must be enforced at the data model level, not the UI level

**Invariant 4 — An insight fires at most once per category per period**
- Statement: The same spend pattern observation must not repeat within the same month or monthly period
- Break scenario: Pattern fires every time the app is opened once threshold is crossed
- Trigger: Missing state tracking for whether an insight has already been surfaced
- Protection note: Insight state must be persisted — not computed fresh on every open

**Invariant 5 — App session must exist before financial writes**
- Statement: Income, charge, and transaction writes require an active app session context
- Break scenario: A write occurs before setup, causing orphan records and invalid aggregates
- Trigger: Missing setup guard in input flow
- Protection note: All write workflows gate on active session presence before persistence

---

## Proposed Architecture

### Components

**AppSessionContext**
- Responsibility: Holds the active app session identity and opening balance, with optional period metadata for planning views.
- Inputs: Setup values (opening balance, optional period label/end target)
- Outputs: Session ID, opening balance, optional period framing for dashboards and history filters
- Ownership: Created once at first setup; period markers can be added later without resetting core history
- Notes: If no active app session exists, the app cannot function — all other components depend on this

**IncomeLog**
- Responsibility: Records all income entries with source type, amount, and date. Provides total income to the balance engine.
- Inputs: Amount, source tag, date
- Outputs: Total income for active session/date range; income by source type; income timeline
- Ownership: Append-only — entries are not edited or deleted after logging
- Notes: Source tags (scholarship / family / work / other) are for pattern analysis and display only — they do not affect the calculation

**CommittedChargeRegister**
- Responsibility: Holds all future payment obligations. Each charge reduces free money immediately at log time. Generates reminders at 3-day threshold.
- Inputs: Charge name, amount, due date, recurring flag, frequency if recurring
- Outputs: Total committed amount; list of upcoming charges sorted by due date; reminder triggers
- Ownership: Charges can be marked as paid (which moves them from upcoming to settled) but amounts do not change retroactively
- Notes: This is the component that makes the core mechanic work — committed charges are deducted here, not at transaction time

**TransactionLog**
- Responsibility: Records all actual spend events. Provides daily and cumulative spend for the on-track calculation and pattern detection.
- Inputs: Amount, description, category tag, date
- Outputs: Today's total spend; spend by category; rolling category averages for pattern detection
- Ownership: Append-only
- Notes: Category tags are optional — the daily number works without them; pattern detection requires them

**BalanceEngine**
- Responsibility: The calculation core. Takes total income, total committed charges, and total transactions to produce free money and the daily safe-to-spend number.
- Inputs: Total income (from IncomeLog); total committed charges (from CommittedChargeRegister); total transactions spent (from TransactionLog); active period context (from AppSessionContext)
- Outputs: Free money; daily safe-to-spend number; on-track boolean; over/under amount for today
- Ownership: Pure calculation — no state of its own; always computed fresh from inputs
- Notes: Must be independently testable with no dependencies on storage or UI

**PatternDetector**
- Responsibility: Analyses transaction history to identify when a category is tracking above its rolling average by a meaningful threshold. Manages insight state to prevent repeat surfacing.
- Inputs: Transaction history by category (from TransactionLog); insight state (which insights have already fired)
- Outputs: Insight text if threshold crossed and insight not yet surfaced; null otherwise
- Ownership: Reads transactions; writes insight state
- Notes: Does not fire until minimum data threshold is met (~14 days). One insight per category per period.

**ReminderScheduler**
- Responsibility: Checks committed charges daily and surfaces a reminder when a charge is 3 days from due date.
- Inputs: CommittedChargeRegister entries; today's date
- Outputs: Reminder message for any charge due in exactly 3 days; null otherwise
- Ownership: Read-only on charges; writes reminder-sent state to avoid duplicate reminders
- Notes: In Stage 1–2 (CLI/CustomTkinter), this runs when the app is opened. In Stage 5 (web), this can be a scheduled check.

### Interaction Summary

When a student opens the app, AppSessionContext provides the active context, IncomeLog and CommittedChargeRegister provide the financial inputs, and BalanceEngine computes the current budget signal in real time. TransactionLog provides today's and monthly spend so the on-track indicator can be shown. ReminderScheduler checks for any charges due in 3 days and surfaces them if present. PatternDetector checks whether a category insight is due and surfaces it if thresholds are met and it has not fired before.

All write operations — logging income, logging a charge, logging a transaction — update their respective components and trigger a BalanceEngine recalculation. The daily number is always fresh, never cached.

---

## Data Ownership and State Model

**AppSession**
- Source of truth: Local storage (JSON in Stage 1–2, PostgreSQL from Stage 3 onwards)
- Mutated by: Student at first setup; optional period metadata may be updated later
- Read by: BalanceEngine and all components for session scoping
- Derived state: Optional period framing when labels/end targets are set
- Lifecycle: Created at first setup; persists continuously unless explicitly archived

**IncomeEntry**
- Source of truth: IncomeLog store
- Mutated by: Student (append only — no edits, no deletes)
- Read by: BalanceEngine (total income)
- Derived state: Total income (sum of entries in active session and selected date range)
- Lifecycle: Created when student logs income; never modified; scoped to app session

**CommittedCharge**
- Source of truth: CommittedChargeRegister store
- Mutated by: Student (create); system (mark as paid when due date passes and student confirms)
- Read by: BalanceEngine (total committed); ReminderScheduler (due dates); UI (upcoming list)
- Derived state: Total committed amount (sum of all active charges)
- Lifecycle: Created when student logs a future charge; marked paid when it clears; recurring charges regenerate for next period automatically

**Transaction**
- Source of truth: TransactionLog store
- Mutated by: Student (append only)
- Read by: BalanceEngine (total spent); PatternDetector (category history); UI (today's spend)
- Derived state: Today's total spend; rolling 14-day average per category
- Lifecycle: Created when student logs a spend; never modified; scoped to app session

**InsightState**
- Source of truth: PatternDetector store
- Mutated by: PatternDetector (writes when an insight fires)
- Read by: PatternDetector (prevents re-firing)
- Derived state: None
- Lifecycle: Created when an insight fires; persists for the monthly period; resets at new month

**ReminderState**
- Source of truth: ReminderScheduler store
- Mutated by: ReminderScheduler (writes when a reminder fires)
- Read by: ReminderScheduler (prevents duplicate reminders for same charge)
- Derived state: None
- Lifecycle: Created when a reminder fires for a given charge; tied to that charge's ID

---

## Trust Boundaries and Security Notes

### Trust Entry Points
- All input comes from the student via CLI or web form — no external data sources in Stages 1–2
- In Stage 5, the web interface introduces a local network trust boundary (localhost or LAN)
- No authentication exists in Stage 1 — the tool is single-user and local only

### Authorization Enforcement
- No multi-user access in Stage 1 — authorization is not relevant
- In Stage 5, if the web dashboard is exposed beyond localhost, basic auth should be added
- The BalanceEngine must not be callable with fabricated inputs from the UI layer — inputs must pass through the data components

### Tenant Isolation
- Not applicable in Stage 1 (single user, local storage)
- If multi-user is ever added, all records must be scoped by user ID from the start — retrofitting this is dangerous

### Sensitive Data and Privileged Operations
- Financial data (income, charges, transactions) is personally sensitive — local storage keeps it off external servers
- No plaintext financial data should appear in logs or error messages
- The CommittedChargeRegister is the most sensitive component — incorrect mutation (e.g. a charge not being deducted) directly produces a misleading daily number

---

## Concurrency and Correctness Notes

| Workflow / State | Risk | What Can Go Wrong | Control Note |
|---|---|---|---|
| Log income while BalanceEngine is reading | Stale read | Daily number computed before new income is counted | In Stages 1–2 (single-user local app), this is sequential — not a real risk. In Stage 5 (web), writes must complete before reads for balance calculation |
| Log a committed charge | Double-deduction | Recurring charge auto-generates next cycle while student manually adds the same due date | Unique constraint on (charge name + due date) within active scope to prevent duplicates |
| Pattern detection threshold | Premature firing | Insight fires before data is statistically meaningful | Enforce minimum data threshold (14 days) as a hard gate before any insight is evaluated |
| Insight state | Re-firing | Same insight fires multiple times because state was not persisted correctly | InsightState must be written to storage immediately when an insight fires — not held in memory |
| Period marker changes | Scope confusion | Student mistakes a planning marker for a hard reset and expects data deletion | Keep period markers optional and non-destructive; history stays continuous by default |
| Committed charge marked paid | Balance inconsistency | Charge marked paid but not removed from committed total | Paid charges must be explicitly removed from the committed sum in BalanceEngine inputs |

---

## Scalability and Multi-Tenancy Notes

### Growth Axes
- Transaction volume per student over continuous use (expected: 5–15 entries/day; monthly archives used for analysis)
- Number of committed charges active at a given time (expected: 5–15)
- Number of optional period markers stored historically

### Likely First Bottlenecks
- None at expected single-student scale in Stages 1–2
- In Stage 5, if the web dashboard runs pattern detection on every page load, performance could degrade with large transaction histories — pattern detection should run on a schedule, not on every request

### Current Sufficiency
- PostgreSQL handles single-student volumes comfortably through Stage 5
- Local storage requires no infrastructure management

### Future Redesign Triggers
- Multi-user support would require migrating from local PostgreSQL to a multi-tenant server database with user scoping
- Push notifications would require a backend service beyond the current architecture
- Multi-currency support would require an exchange rate API integration and currency conversion layer

### Tenant / Noisy-Neighbour Notes
- Not applicable — single user, local storage

---

## Risks and Failure Notes

| Risk | Failure Shape | Cause | Note |
|---|---|---|---|
| Student does not log transactions consistently | Daily number becomes inaccurate; pattern detection cannot fire | Manual logging friction; forgetting during busy periods (exams) | Mitigate with frictionless logging UX — minimum required fields; quick-log shortcut is a Stage 2 CustomTkinter priority |
| Student logs a charge with wrong due date | Reminder fires at wrong time; charge deducted from wrong period | Human error at input | Allow charge editing; surface upcoming charges list prominently so errors are visible |
| Optional period marker set incorrectly | Student reads the wrong planning window | Human error at period setup | Allow marker edits and keep all calculations reproducible from raw records |
| Free money goes negative silently | Student believes they have more than they do; app fails its core purpose | More committed charges logged than income | This must be an explicit warning state — the most important failure mode to handle visually |
| Pattern detection fires too early | Insight is statistically meaningless; student loses trust in the feature | Threshold set too low; minimum data gate not enforced | Enforce 14-day minimum strictly; prefer false negatives over false positives for insights |
| Data loss from storage corruption | All data lost | JSON or PostgreSQL corruption; accidental deletion | Document how to back up data; consider automatic backup on session close from Stage 3 onwards |

---

## Alternatives Considered

### Alternative 1 — Monthly budget reset instead of academic year scope
**Description:** Standard monthly budgeting model where the budget resets on the 1st of each month.
**Why plausible:** Every mainstream budgeting app uses monthly budgeting; it maps to how bills work.
**Main advantages:** Familiar mental model; easier to understand for first-time users.
**Main disadvantages:** Completely wrong for a student whose income arrives at the start of an academic year as a lump sum. A monthly reset would make the app treat scholarship money as if it regenerates every month — it does not. The semester-scope model is the only one that correctly represents student financial reality.
**Why not chosen:** The academic year is the natural financial period for this user. Monthly scoping would make the daily number wrong.

### Alternative 2 — Automatic bank feed via Plaid or open banking API
**Description:** Connect directly to the student's bank account to pull transactions automatically.
**Why plausible:** This is how Mint, Emma, and Cleo work; it removes the manual logging burden.
**Main advantages:** No manual entry; always accurate; can detect charges the student forgot about.
**Main disadvantages:** Requires API access to Israeli banks (limited open banking infrastructure); introduces external dependency and cost; adds authentication complexity; app becomes useless if API access fails; still cannot predict future committed charges — it only sees what has already cleared.
**Why not chosen:** Israeli open banking is not mature enough to rely on; manual logging keeps the project buildable as a student project; bank feed does not solve the core problem (future charge visibility) anyway.

### Alternative 3 — AI-powered natural language interface
**Description:** Student types "I spent ₪45 on groceries" instead of filling a form; AI parses and logs the transaction.
**Why plausible:** Reduces friction; feels modern; fits the fintech trend of conversational finance.
**Main advantages:** Lower logging friction; more natural interaction.
**Main disadvantages:** Introduces external API dependency and cost; adds latency to every transaction log; parsing errors create silent data corruption; the core value is the calculation, not the input method.
**Why not chosen:** Deferred to Stage 5 as a polish feature — the math is the intelligence, not the interface.

### Explicit Tradeoffs in the Chosen Design
- Manual logging in exchange for: no external dependencies, works offline, student controls all data
- Continuous session scope in exchange for: needs clear period markers to preserve planning context
- Local storage in exchange for: no sync across devices, no cloud backup
- No bank integration in exchange for: future committed charges visible (which bank feeds cannot show)
- Pattern detection with high threshold in exchange for: fewer false positives, more trustworthy insights

---

## Rollout / Migration Notes

1. **Stage 1 (CLI + JSON):** No deployment needed — runs locally. The student is the only user. Data lives in JSON files. This stage is complete when all core calculations, services, and JSON adapters work correctly and are fully tested.

2. **Stage 1 → Stage 2 (CustomTkinter desktop dashboard):** `app/cli.py` is replaced by a **CustomTkinter** desktop GUI application. The app opens immediately to a live dashboard window — no commands to type. Buttons and modal input forms handle all input (add income, log charge, log spend, mark paid). The domain layer, services, and JSON repositories are completely untouched — only the interface layer changes. JSON storage remains. This stage is complete when the app opens to a working dashboard and every Stage 1 workflow is reachable from the UI.

3. **Stage 2 → Stage 3 (PostgreSQL persistence):** JSON adapters in `infrastructure/json/` are replaced by PostgreSQL adapters in `infrastructure/postgres/`. A one-time migration script converts existing JSON data. The GUI and all services are untouched — storage is swapped underneath. This stage is complete when all data survives app restarts correctly via PostgreSQL.

4. **Stage 3 → Stage 4 (reminders + pattern detection):** New `ReminderScheduler` and `PatternDetector` components added. New `InsightState` entity added to the schema. The CustomTkinter dashboard gains a notification area and an Occurrences screen. Existing transaction data automatically feeds the detector. Rollback is safe — removing these components does not affect core calculations.

5. **Stage 4 → Stage 5 (web UI):** FastAPI backend wraps the existing service layer. A React or Streamlit frontend replaces or supplements the CustomTkinter dashboard. The CustomTkinter dashboard continues to function independently. Deployment is localhost only at this stage.

6. **Stage 5 → Stage 6 (optional: local bank connectivity):** Read-only connection to the student's local Israeli bank account to automatically import cleared transactions. Manual logging remains as the primary path. No architectural changes to core logic required — bank-imported transactions feed into the existing TransactionLog.

**Rollback concern for all stages:** Because each stage is independently functional, rolling back means stopping at the previous stage. No stage destroys the functionality of the one before it.

---



---


---


---


---


---


---


---

## Future Features — Contextual Discovery

*Planned beyond the current core stages. Noted here to prevent premature building and to preserve the idea clearly.*

### What it is

A layer of external, location-aware information surfaced at the moment it is most relevant to the student's financial situation. Unlike the rest of the app — which works entirely on the student's own data — contextual discovery requires external data sources and location permissions.

### Planned features

**Nearby cheaper supermarkets**
If the student consistently overspends on groceries, the app surfaces discount supermarket options near their campus or home. Relevant Israeli chains: Rami Levy, Osher Ad, Victory. Trigger: grocery spend tracking 30%+ above monthly average. Output: one sentence, once — "Rami Levy is 400m from your campus and typically 15–20% cheaper on basics."

**Student discounts nearby**
Shops, cafes, transport operators, and services within a defined radius that offer student pricing the student may not know about. Shown the first time the student logs a spend in a category where a nearby student discount exists.

**Housing listings**
When rent is flagged as the dominant budget pressure (>40% of monthly budget), surface relevant Yad2 or Madlan listings for shared apartments or university dorms near the student's university. One listing type, relevant to their city, shown once.

### Why this is deferred

| Reason | Detail |
|---|---|
| External data dependency | Requires supermarket price APIs, location services, housing listing APIs — none in the current architecture |
| Location permissions | A new trust boundary — student must explicitly grant location access |
| Israeli-specific data | Supermarket chains, dorm availability, and student discount programmes require local data partnerships |
| Premature complexity | Building this before the core stages are stable would distract from the core product |

### Design principle when built

Surface one relevant thing at the right moment. Not a directory. Not a list of 20 options. If the student just logged high grocery spend and a cheaper supermarket is 400 metres away, that is one sentence. Once. Consistent with the behavioural nudge philosophy throughout the app.


---

## Weakness 6 Resolution — Pattern Detection Threshold

*Resolved April 2026. Replaces the placeholder in the pre-review weakness check.*

### Philosophy — conservative defaults, empirically adjusted

Thresholds for pattern detection cannot be determined correctly before real usage data exists. Guessing produces arbitrary numbers that either fire too often (eroding trust) or never fire at all (being useless). The correct approach is: set conservative defaults now, observe real behaviour in Stage 4, and adjust based on actual student data.

### Minimum data gate — C (14 days AND 20 transactions)

Before pattern detection runs at all, both conditions must be true:

- At least **14 calendar days** have passed since the first logged transaction
- At least **20 transactions** have been logged in total across all categories

This prevents the detector from firing on thin data. A student who logs 2 transactions in 14 days has no meaningful pattern yet. A student who logs 20 transactions in 3 days also has no meaningful pattern — they need time variance too.

Both conditions are hard gates. If either fails, PatternDetector returns null — no insight, no message, no indication to the student that detection is running.

### Spike threshold — deferred to Stage 4

The percentage above rolling average that triggers an insight is **not set in stone now**. It will be determined empirically during Stage 4 development using real logged transaction data.

**Conservative starting point for Stage 4 testing:** A category spend that is tracking 50% above its rolling monthly average AND is on pace to exceed that average by end of month. This will be tested, observed, and adjusted before the feature is considered done.

This is not a weakness — it is the correct engineering approach for a threshold that only makes sense with real data.

### Minimum active categories — deferred to Stage 4

The minimum number of categories with sufficient transactions to make pattern detection meaningful is also deferred to Stage 4 empirical observation.

**Conservative starting point:** At least 2 distinct categories must have 5 or more transactions each before any category-level insight fires. A student who tags everything as "other" will not receive insights — the data is not granular enough.

### What is locked now

| Parameter | Decision |
|---|---|
| Minimum days | 14 calendar days — hard gate |
| Minimum transactions | 20 total — hard gate |
| Spike threshold | Conservative default of 50% above rolling average — empirically adjusted in Stage 4 |
| Minimum active categories | 2 categories with 5+ transactions each — empirically adjusted in Stage 4 |
| False negative preference | Always prefer no insight over a premature one — trust is more valuable than frequency |

### INV-4 update

INV-4 now has a concrete data gate: PatternDetector must check both the 14-day and 20-transaction conditions before evaluating any threshold. If either gate fails, the function returns null immediately. This gate check is the first operation in the PatternDetector — not an afterthought.


---

## Weakness 5 Resolution — Period Transition and History

*Resolved April 2026. Replaces the placeholder in the pre-review weakness check. Also removes the hard academic year boundary as the app scope.*

### No forced reset — the app runs continuously

The app does not require the student to start a new academic year. It keeps running indefinitely. A student who graduates, takes a gap year, finds a job, or simply never thinks to reset will not be penalised — their data and patterns continue uninterrupted.

If the student wants to mark a new period (a new academic year, a new job, a life change), they can optionally create a named period in settings. This triggers an automatic archive of the previous period's data and starts a fresh committed charge register and income log. This is optional, not required.

### The real scope boundary is calendar months, not academic years

The app thinks in calendar months. The student can optionally think in academic years — but the app does not enforce it. This simplifies the entire design:

- No academic year end date required at setup
- No division-by-zero risk from a passed end date
- PatternDetector runs indefinitely without reset
- History is always available as far back as the student has used the app

**Setup changes:** Instead of entering an academic year start and end date, the student only enters their opening balance at first use. The app begins tracking from that point forward.

### History view — month by month, custom date ranges

The history screen shows every calendar month since the student started using the app. For each month:
- Monthly budget (income − committed charges for that month)
- Actual spend
- On-track state for that month
- Month-end balance

The student can also set a custom date range to view any arbitrary period — for example, October to June to approximate an academic year, or September to September for a calendar year. This is a filter on the history view, not a structural change to the data.

### PatternDetector — runs continuously

No reset at any boundary. The detector runs on the full rolling transaction history. It gets smarter the longer the student uses the app. Monthly insight scoping (INV-4) still applies — one insight per category per calendar month — but the underlying data window grows indefinitely.

### Data model update — AcademicYearContext removed

AcademicYearContext is replaced by a simpler **AppSession** entity:

| Field | Type | Description |
|---|---|---|
| start_date | date | Date the student first set up the app |
| opening_balance | decimal | Balance at first setup |

No end date. No hard boundary. The app runs until the student stops using it.

Committed charges, income entries, and transactions are no longer scoped to an academic year — they are scoped to the app session and filtered by date when needed.

### INV-5 update

INV-5 (academic year end date cannot be in the past) is now retired. It no longer applies — there is no mandatory end date.


---

## Weakness 4 Resolution — Fuzzy Charge Resolution Flow

*Resolved April 2026. Locks the Stage 1 CLI behaviour; the Occurrences screen remains a Stage 2 presentation layer.*

### Stage 1 CLI resolution flow

Fuzzy charges are created with a known date and an optional estimate, then stay pending until the student confirms or discards them. Stage 1 exposes that behaviour through the CLI; Stage 2 may later present the same states in an Occurrences screen.

### Scenario A — Normal resolution (alert fires, amount known)

1. Alert fires 3 days before fuzzy charge due date
2. Student confirms the amount with `fuzzy-charge resolve` or removes the entry with `fuzzy-charge discard`
3. The estimated amount logged at creation is pre-filled as context — the student confirms the final amount explicitly
4. **Resolve:** Fuzzy charge converts to a committed charge or income entry, depending on direction. The confirmed amount is applied immediately and the pending record is removed.
5. **Discard:** Fuzzy charge is removed entirely. No deduction or credit happens.
6. **Dismiss:** The reminder can be ignored for now; the fuzzy charge stays pending until the student acts later.

If the estimated amount was wrong, the student deletes and re-logs the charge as a new entry with the correct amount.

### Scenario B — Late resolution (due date passes, charge unresolved)

The fuzzy charge remains pending after the due date. It is never auto-discarded. The student can still resolve or discard it later, and Stage 2 can present overdue items in a muted style once the GUI exists.

### Scenario C — Charge never arrives

The student realises the charge will not happen and discards it. The fuzzy charge is removed with no deduction or credit. If confirmation is needed later in the GUI, a brief prompt can ask: "Remove this charge? It will not affect your balance."

### FuzzyCharge states

| State | Display | Trigger | Resolution |
|---|---|---|---|
| Pending — upcoming | Normal display in Occurrences | Logged, due date in the future | Confirm or Delete |
| Pending — alert window | Notification fires | 3 days before due date | Confirm, Delete, or ✕ dismiss |
| Pending — overdue | Gray / muted in Occurrences | Due date passed, unresolved | Confirm or Delete |
| Resolved | Removed from Occurrences | Student confirmed amount | Converts to CommittedCharge, deducts |
| Discarded | Removed from Occurrences | Student deleted | No deduction, gone |

### Data model update — FuzzyCharge

FuzzyCharge gains two new fields:

| Field | Type | Description |
|---|---|---|
| estimated_amount | decimal, nullable | Optional rough estimate entered at creation. Pre-filled in confirmation prompt. Never used in calculations. |
| status | enum | pending / overdue / resolved / discarded |

### Design deferred to Stage 2

The exact visual treatment of pending and overdue fuzzy charges, the Occurrences screen layout, and the notification prompt UI are deferred to Stage 2 (CustomTkinter dashboard). What is locked now: the behaviour, the states, the resolve/discard flow, and the ability to leave a fuzzy charge pending until later.


---

## Weakness 3 Resolution — On-Track Threshold Definition

*Resolved April 2026. Defines the monthly balance signal used by the dashboard and lock-step calculations.*

### Monthly model — not daily

The core budget signal is monthly, not daily. Students do not spend uniformly every day — a textbook purchase, a doctor visit, or a social event can consume several days of a daily budget without the student being financially irresponsible. The monthly model reflects how students actually live.

**Core formula update — BalanceEngine:**

    income_this_month  = sum of income entries dated this calendar month
    charges_this_month = sum of committed charges due this calendar month
    monthly_budget     = income_this_month − charges_this_month
    monthly_spent      = sum of transactions logged this calendar month
    monthly_left       = monthly_budget − monthly_spent
    on_track_pct       = monthly_spent ÷ monthly_budget × 100

### Dashboard view — progress bar (Option A)

The dashboard shows a visual progress bar:

    ₪[monthly_spent] of ₪[monthly_budget] used this month

The bar fills as the student spends. The colour of the bar reflects the on-track state. Exact visual treatment deferred to Stage 2 (CustomTkinter dashboard).

### Three-state on-track signal — percentage-based

| State | Trigger | Meaning |
|---|---|---|
| Green | monthly_spent < 100% of monthly_budget | On track |
| Yellow | monthly_spent between 100% and yellow_threshold% | Slightly over — still within the month |
| Red | monthly_spent > red_threshold% or free money ≤ ₪0 | Significantly over |

**Default thresholds:**
- Yellow triggers at **110%** (10% over monthly budget)
- Red triggers at **130%** (30% over monthly budget)

App estimates these defaults based on historical spend variance once sufficient data exists. Student can override both manually at any time.

### Months remaining — calendar months by default

Months remaining is calculated from the active planning window (including the current partial month when a period marker exists). Students can switch to 30-day blocks in settings if preferred.

### Two views — monthly and period history

**Primary view (home screen):** This month only. Monthly budget, monthly spend, progress bar, on-track state. This is what the student sees every time they open the app.

**Secondary view (period history):** An optional screen showing a month-by-month summary of completed months in the selected date range. Student navigates here intentionally. Shows monthly budget vs actual spend per month, and cumulative totals for the selected range.

### Two types of negative — treated differently

**Type 1 — Monthly deficit** (charges due this month exceed income this month):
Shown on the home screen. The student is tight this month specifically. Common when a scholarship arrives next month but charges are due now. Yellow or red state on the progress bar for this month. The student can see next month's expected income in the period history view to understand why it resolves.

**Type 2 — Overall selected-range deficit** (total committed charges exceed total income across the selected range):
Surfaced in the period history view, not forced onto the home screen every session. This is the crisis state from Weakness 1 — red balance display, full ranked spending breakdown. The student accesses this when they choose to look at the full picture.

### BalanceEngine output — updated

BalanceEngine now produces six output values:

1. Free money (selected range — ₪ amount)
2. Monthly budget (this calendar month — ₪ amount)
3. Monthly spent (this calendar month — ₪ amount)
4. Monthly left (monthly_budget − monthly_spent)
5. On-track state (green / yellow / red)
6. Balance state (normal / caution / crisis — from Weakness 1 resolution)


---

## Weakness 2 Resolution — Recurring Charge Auto-Generation Behaviour

*Resolved April 2026. Matches the Stage 1 command flow and persists the next charge immediately on payment.*

### When the next occurrence is created

Immediately when the student marks the current occurrence as paid. The next occurrence is created in the CommittedChargeRegister at that exact moment and deducts from free money immediately — consistent with INV-3.

There is no delay, no queue, no just-in-time creation. The student marking rent as paid on the 2nd means next month's rent appears and deducts on the 2nd, not on the 1st of next month.

### Student notification on auto-generation

When a recurring charge auto-generates, the app surfaces a quiet notification:

> *"Next [charge name] (₪[amount]) has been scheduled for [date] — already counted in your balance."*

No action required. The student is informed, not asked. This is consistent with the app's philosophy: informed, never surprised, never blocked.

### Per-charge reminder lead time

Each recurring charge carries its own reminder lead time — how many days before the due date the reminder fires. This is a new field on CommittedCharge:

- **Global default:** 3 days (set at academic year setup, matches the app-wide default)
- **Per-charge override:** Student can change the lead time for any individual charge (e.g. rent might warrant 5 days, a small subscription only 1 day)
- The reminder fires once per occurrence. If the student has already seen it, it does not repeat.

### Data model update — CommittedCharge

CommittedCharge gains one new field:

| Field | Type | Description |
|---|---|---|
| reminder_days | integer | Days before due date to fire reminder. Default: global setting. Student-overridable per charge. |

### Behaviour summary

| Event | What happens |
|---|---|
| Student marks charge as paid | Next occurrence created immediately; free money decreases immediately; auto-generation notification fires |
| reminder_days before next due date | Reminder fires: "[charge] due in [N] days — already in your balance" |
| Student opens app any other time | No notification for this charge until reminder window |


---

## Weakness 1 Resolution — Free Money State System

*Resolved April 2026. Replaces the placeholder "explicit warning state" in INV-1 and the pre-review weakness check.*

### Three-state balance display

| State | Trigger | Daily Number | Visual |
|---|---|---|---|
| Normal | Free money > threshold | Calculated normally | Standard display |
| Caution | Free money ≤ student threshold | Calculated normally | Yellow highlight on balance area |
| Crisis | Free money ≤ 0 | Shows ₪0 | Red highlight on balance area; actual negative shown beneath |

The student is never blocked from using the app in any state. The app shows reality — it does not restrict behaviour.

### Threshold — app suggests, student overrides

At first setup, the app calculates a suggested caution threshold as **7 × estimated average daily spend** (one week buffer). The student can:
- Accept the suggested threshold
- Override it with a custom amount
- Set it to zero to disable the yellow caution state entirely

The threshold applies only to the yellow state. The red crisis state always triggers at free money ≤ ₪0, regardless of threshold setting.

Threshold is stored as a new data entity — **BalanceThreshold** — set at setup, editable at any time.

### Crisis state — full ranked spending breakdown

When free money is zero or negative, the app surfaces a complete ranked breakdown of all spending categories for the current month. All categories shown, ordered by amount spent. No advice. No judgment. The data speaks for itself.

This reuses existing TransactionLog category data via a new trigger context on the PatternDetector — it is not a new component.

### Crisis state — persistence behaviour

The red highlight persists on the balance display area for as long as free money is zero or negative. It is not a modal or banner — it cannot be dismissed. It disappears automatically when free money returns to positive. The precise visual treatment (exact colours, border, animation) is deferred to Stage 2 (CustomTkinter dashboard).

### BalanceEngine output update

BalanceEngine now produces four output values:
1. Free money (₪ amount)
2. Daily safe-to-spend number (₪0 if crisis)
3. On-track boolean
4. **Balance state** (normal / caution / crisis)

### INV-1 update

INV-1 is now fully specified: free money is never displayed without a corresponding state signal. The three-state system is the enforcement mechanism.

## Pre-Review Weakness Check *(working note — not part of design file)*

Sections that need strengthening before formal review:

- **Pattern detection threshold** — "approximately 14 days" is still a working assumption. The actual threshold (number of transactions, number of categories, percentage deviation) needs to be made concrete before implementation.
- **Recurring charge behaviour** — resolved in Weakness 2; tracked here only for implementation verification.
- **Free money goes negative** — resolved in Weakness 1; tracked here only for implementation verification.
- **Period marker UX** — optional period labels are defined, but the exact UI guidance for when to create one still needs user-tested wording.
- **Pattern threshold calibration** — hard gates are set, but the final over-average trigger still needs empirical tuning in Stage 4.

---

*Design file assembled following the xperience.works methodology.*
*First draft — ready for deeper review.*
*Last updated: April 2026*
