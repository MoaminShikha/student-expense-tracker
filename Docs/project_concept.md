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
- **AppSession** — replaces AcademicYearContext. Fields: start_date and opening_balance. No end date.

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

---

## Fintech Reference Library

### What is PFM — Personal Finance Management

PFM is the fintech category this product belongs to. It covers software that helps users manage money across budgeting, expense tracking, and future payment planning.

| Source | What it covers |
|---|---|
| [Personetics — What Is PFM?](https://personetics.com/resource-center/what-is-pfm-what-is-personal-financial-management-personetics-com/) | Industry-level definition of PFM, use cases, and how banks and fintechs implement it |
| [MX — What Is PFM?](https://www.mx.com/blog/what-is-pfm/) | Benefits and use cases; how PFM tools differ from raw banking apps |
| [Moneythor — Back to Basics: What Is PFM?](https://www.moneythor.com/analysis-opinions/back-to-basics-what-is-personal-financial-management-pfm/) | Deep-dive on PFM as a digital banking discipline |
| [Bankrate — What Is Personal Finance Management?](https://www.bankrate.com/banking/what-is-pfm/) | Plain-English overview of PFM features and why they matter to consumers |
| [Wikipedia — Personal Financial Management](https://en.wikipedia.org/wiki/Personal_financial_management) | Category overview, history, and major app examples |

---

### Cash-Flow Forecasting — The Core Mechanic

Cash-flow forecasting is what this app does for an individual: project when money comes in and goes out, and surface mismatches before they cause overdrafts. The committed vs free money separation is a personal implementation of this corporate finance concept.

| Source | What it covers |
|---|---|
| [SavePoint Finance — Cash Flow Forecasting for Personal Finance](https://savepointfinance.com/blog/cash-flow-forecasting-personal-finance) | How individuals can apply business cash-flow forecasting to their own money |
| [SmartAsset — Cash Flow Planning and Budgeting](https://smartasset.com/financial-advisor/cash-flow-planning) | Practical guide to personal cash-flow planning and budgeting |
| [Association of Corporate Treasurers — Cash-Flow Modelling for Personal Finance](https://www.treasurers.org/hub/treasurer-magazine/have-you-considered-cash-flow-modelling-to-forecast-your-own-future-finances) | Treasury professionals explain why cash-flow modelling matters for individuals, not just companies |
| [Satty & Partners — Personal Cash Flow Statement Guide](https://satty.com/blog/guide-to-using-a-personal-cash-flow-statement) | How to read and use a personal cash-flow statement |

---

### Behavioural Nudges in Fintech

The pattern detection feature (Stage 4) is a behavioural nudge — one relevant insight at the right moment, not a lecture. This is a well-researched fintech design principle.

| Source | What it covers |
|---|---|
| [NYU Stern — Fintech Nudges (Research Paper)](https://www.stern.nyu.edu/experience-stern/about/departments-centers-initiatives/centers-of-research/fubon-center-technology-business-and-innovation/research/research-papers/doctoral-fellow-research/fintech-nudges) | Academic research showing fintech nudges reduce overspending by ~5% per day — and the risk of the ostrich effect |
| [SSRN — Fintech Nudges: Overspending Messages and PFM](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3390777) | Full research paper on measurable impact of spending nudge messages |
| [The Decision Lab — The Unfulfilled Promise of Behavioural Science in Fintech](https://thedecisionlab.com/insights/finance/the-unfulfilled-promise-of-behavioral-science-in-fintech) | Critical perspective: why most fintech nudges fail and what good ones do differently |
| [Medium — Behavioural Design in Finance](https://medium.com/nudge-notes/behavioral-design-in-finance-encouraging-sound-money-decisions-b0ca6a925127) | How to design financial nudges that actually change behaviour |
| [BehavioralEconomics.com — Personal Finance](https://www.behavioraleconomics.com/tag/personal-finance/) | Research hub for behavioural economics applied to personal finance |

---

### Clean Architecture in Fintech Software

The architecture pattern used in this project — layered, protocol-based, dependency-inverted — is how production financial software is structured. This is not over-engineering; it is the standard.

| Source | What it covers |
|---|---|
| [Uncle Bob — The Clean Architecture (Original)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) | The original article by Robert C. Martin defining Clean Architecture |
| [DEV.to — Building Secure and Scalable Fintech Applications](https://dev.to/ojosolomon/building-secure-and-scalable-fintech-applications-a-technical-architecture-deep-dive-35in) | How Clean Architecture applies specifically to fintech — security, scalability, and domain isolation |
| [Nimble AppGenie — Fintech App Architecture Guide](https://www.nimbleappgenie.com/blogs/fintech-app-architecture/) | Principles and architecture patterns used in real fintech apps |
| [Cogent — Clean vs Hexagonal vs Layered Architecture](https://cogentinfo.com/resources/designing-scalable-secure-applications-choosing-between-clean-hexagonal-and-layered-architectures) | When to choose each pattern — fintech context |
| [Bitloops — Clean Architecture Reference Guide](https://bitloops.com/docs/bitloops-language/learning/software-architecture/clean-architecture) | Comprehensive reference covering all layers, rules, and tradeoffs |

---

### Fintech Terminology Glossary

Key terms used in this project and their fintech definitions.

| Term | Definition |
|---|---|
| **Free money** | The portion of income remaining after all committed upcoming charges are deducted. The honest spendable amount. |
| **Committed funds** | Money already allocated to a known future obligation — rent, tuition, subscriptions. Deducted at log time, not at clearing time. |
| **Burn rate** | The rate at which available money is being consumed. In personal finance: monthly spend relative to monthly budget. |
| **Cash-flow forecasting** | Projecting the timing and size of future inflows and outflows to identify shortfalls before they occur. |
| **Available balance vs ledger balance** | Available balance = what you can spend now. Ledger balance = total including pending debits not yet cleared. Your bank shows ledger; this app shows available after committed charges. |
| **On-track state** | A classification of whether current-month spending is within budget (green), slightly over (yellow), or significantly over (red). |
| **Behavioural nudge** | A low-friction prompt that surfaces relevant information at the right moment to influence a financial decision — without restricting choice. |
| **PFM** | Personal Finance Management — fintech category covering tools that help individuals track, plan, and understand their money. |
| **Reconciliation** | The process of matching logged entries against actual bank activity to ensure nothing is missed or double-counted. |
| **Runway** | How long current funds will last at the current burn rate. `free_money ÷ average_monthly_spend`. |

**Glossary references:**
- [Arc — FinTech Glossary of Terms](https://www.joinarc.com/glossary)
- [Weavr — Fintech Glossary of Terms](https://www.weavr.io/blog/fintech-glossary-of-terms/)
- [Funding Options — Fintech Glossary: Key Business Finance Terms](https://www.fundingoptions.com/blog/education/fintech-glossary-key-business-finance-terms-explained/)
- [GrowishPay — Fintech Glossary A to Z](https://growishpay.com/glossary/)
- [MyCSBin — Glossary of Cash Flow Terms](https://blog.mycsbin.com/glossary-of-cash-flow-terms)

---

### Student Fintech — Market Context

| Source | What it covers |
|---|---|
| [University of Phoenix — How to Use Fintech Apps for College](https://www.phoenix.edu/articles/finance/how-to-use-fintech-apps-for-college.html) | Student-specific fintech use cases and recommended approaches |
| [Verified Market Research — Personal Finance Apps Market](https://www.verifiedmarketresearch.com/product/personal-finance-apps-market/) | Market size, growth projections, and student segment data |
| [Built In — 17 Top Fintech Apps to Know](https://builtin.com/articles/fintech-apps) | Overview of the competitive landscape this product sits within |
| [Global Fintech Series — What Is PFM?](https://globalfintechseries.com/finance/what-is-personal-financial-management-pfm/) | PFM as a growing fintech sub-category with student segments |

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

*Delivers: a complete CLI tool with all core logic, services, and JSON persistence tested.*

### Stage 2 — CustomTkinter Dashboard
- Replace CLI with a CustomTkinter desktop GUI application
- App opens directly to a live dashboard window — no commands to type
- Buttons and modal forms for all input (income, charges, spend, mark paid)
- Domain, services, and JSON repositories untouched — interface layer only

*Delivers: a real app feel — opens to a dashboard, usable without knowing terminal commands.*

### Stage 3 — PostgreSQL Persistence
- Replace JSON file adapters with PostgreSQL adapters
- One-time migration script converts existing JSON data
- CustomTkinter dashboard and all services untouched — storage swapped underneath
- No feature logic changes

*Delivers: nothing lost between sessions, production-grade storage.*

### Stage 4 — Reminders and Pattern Detection
- Upcoming charge reminders (T-3 days)
- Fuzzy charge date alerts and follow-up prompts in the Occurrences screen
- Pattern detection with hard gates (14 days AND 20 transactions)
- One surfaced observation per category per calendar month
- False negative preference — no premature insights

*Delivers: the core promise — notified before a charge hits, the app notices things the student hasn't noticed.*

### Stage 5 — Web UI
- FastAPI backend wrapping existing service layer — unchanged
- React or Streamlit frontend: progress bar, monthly number, Occurrences, history
- CustomTkinter dashboard continues to work independently
- Deployment is localhost only

*Delivers: the shareable portfolio piece.*

### Stage 6 — Advanced Integrations
- Local bank connectivity (read-only OFX/CSV import)
- Multi-currency support (NIS + USD/EUR via exchange rate API)
- Natural language transaction entry
- Other optional expansions — added only if they solve a real problem

*Delivers: production-grade. Optional, additive, never breaking.*


---

## Future Vision (beyond Stage 7)

Features that belong to the product's long-term roadmap but are deliberately outside the current build scope. They are noted here so they are not forgotten and not accidentally built too early.

### Contextual discovery — nearby savings

The app knows the student's spending patterns. A future stage could use location context to surface genuinely relevant local information:

- **Nearby cheaper supermarkets** — if the student consistently overspends on groceries, the app could surface discount options (Rami Levy, Osher Ad, local shuk) near their current location or university campus
- **Student discounts nearby** — shops, cafés, transport, and services within walking distance that offer student pricing the student may not know about
- **Housing listings** — when a student's rent is flagged as a major budget pressure, surface relevant dorm availability or shared apartment listings near their university (Yad2, Madlan integration)

This feature is fundamentally different from the rest of the app: it requires **external data sources** (location APIs, supermarket data, housing APIs), **location permissions**, and **Israeli-specific data partnerships**. It should not be built until Stages 1–7 are stable and the core tracking product is genuinely useful on its own.

The design principle for when it is built: **surface one relevant thing at the right moment** — not a directory, not a list of 20 options. If the student just logged ₪340 on groceries and the app knows a cheaper supermarket is 400 metres away, that is one sentence worth saying. Once.

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

*Last updated: April 2026 — v1.5: future vision added — contextual discovery (nearby stores, housing), external data stage noted beyond Stage 7*
