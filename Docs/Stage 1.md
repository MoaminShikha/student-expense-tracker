# Stage 1 Implementation Plan
## Student Expense Tracker — CLI Core

> Stage 1 delivers a complete, fully-usable CLI tool. Every decision made here must survive untouched through Stages 2–7.
> No reminders, no summaries, no web UI, no insights. Just the data model, the calculations, and the commands.

### Current checkpoint (2026-04-15)
- Phase A and Phase B are complete.
- Phase C is in progress: `IncomeService.add_income`, `ChargeService.add_charge`, `ChargeService.add_recurring_charge`, and recurring `ChargeService.mark_paid` behavior are implemented with unit tests.
- Full `tests/unit` status at this checkpoint: `101 passed`.
- Live implementation tracking is maintained in `Docs/stage1_implementation_status.md`.

---

## What Stage 1 Delivers

A command-line tool that:
- Creates a session with an opening balance
- Logs income from multiple sources
- Logs committed charges (one-off, recurring, and fuzzy)
- Logs daily spending
- Calculates and displays free money and monthly on-track state

**Definition of done:** A student can run `session init`, log their rent and scholarship, log a coffee, and see an honest number telling them whether they are on track this month.

---

## Scope Boundaries

### In scope
- `AppSession` — continuous session model, no forced reset
- `IncomeEntry` — income with source tags
- `CommittedCharge` — one-off future payments
- `RecurringRule` — recurring charge definition and next-occurrence generation
- `FuzzyCharge` — date-known, amount-unknown charges
- `Transaction` — actual spend events with optional category
- `BalanceEngine` — free money, monthly budget/spent/left, on-track state, balance state

### Stage boundary — what is not built here

```mermaid
graph LR
    S1[Stage 1\nCLI Core]:::done --> S2[Stage 2\nCustomTkinter\nDashboard]:::out
    S2 --> S3[Stage 3\nPostgreSQL]:::out
    S3 --> S4[Stage 4\nReminders +\nPatterns]:::out
    S4 --> S5[Stage 5\nWeb UI]:::out
    S5 --> S6[Stage 6\nIntegrations]:::out

    classDef done fill:#1a6b3c,stroke:#1a6b3c,color:#fff
    classDef out fill:#f2f2f0,stroke:#ccc,color:#999
```

---

## Architecture

Four strict layers. No layer may depend on a layer above it.

```mermaid
graph TD
    CLI["cli.py\nParses input · calls services · prints output\nNo business logic allowed"]
    SVC["services.py\nOrchestrates use cases · enforces business rules\nCombines models + validators + calculations + repos"]
    DOM["models.py + validators.py\nEntities · value objects · invariants · validation"]
    CALC["calculations.py\nPure BalanceEngine · deterministic · no side effects"]
    REPO["repository.py\nProtocol interfaces + concrete file adapter\nSwappable in Stage 2"]

    CLI -->|calls| SVC
    SVC -->|validates via| DOM
    SVC -->|computes via| CALC
    SVC -->|persists via| REPO

    style CLI fill:#fef3c7,stroke:#92400e,color:#451a03
    style SVC fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a
    style DOM fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    style CALC fill:#dcfce7,stroke:#15803d,color:#14532d
    style REPO fill:#ccfbf1,stroke:#0f766e,color:#134e4a
```

### Module dependency graph

```mermaid
flowchart LR
    CLI[cli.py] --> SVC[services.py]
    SVC --> VAL[validators.py]
    SVC --> CALC[calculations.py]
    SVC --> MOD[models.py]
    SVC --> REPO[repository.py]
    REPO --> MOD
    VAL --> MOD

    style CLI fill:#fef3c7,stroke:#92400e,color:#451a03
    style SVC fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a
    style CALC fill:#dcfce7,stroke:#15803d,color:#14532d
    style VAL fill:#fee2e2,stroke:#b91c1c,color:#7f1d1d
    style MOD fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    style REPO fill:#ccfbf1,stroke:#0f766e,color:#134e4a
```

### Module responsibilities

| File | Responsibility |
|---|---|
| `main.py` | Entrypoint — boots app, delegates to CLI routing |
| `cli.py` | Parses commands, calls services, prints output. No business logic. |
| `services.py` | Orchestrates use cases. Combines models, validators, calculations, repositories. |
| `models.py` | Domain entities and value objects |
| `validators.py` | Input validation and domain constraint enforcement |
| `calculations.py` | Pure `BalanceEngine` logic — deterministic, no side effects |
| `repository.py` | Repository protocols (interfaces) + concrete file-based adapter |

### Key design rules
- **Money:** `Decimal` only — no `float` anywhere in the codebase
- **Dates:** single centralised date utility — no raw `datetime` scattered across modules
- **Interfaces:** `typing.Protocol` for all repository contracts — implementations are swappable
- **CLI is thin:** CLI never mutates domain state directly. All writes go through service methods.
- **Services are pure orchestrators:** no storage details, no formatting, no print statements
- **Calculations are pure functions:** `BalanceEngine` takes inputs, returns outputs, touches no state

---

## Data Model

### Entity relationships

```mermaid
erDiagram
    AppSession {
        uuid session_id PK
        date start_date
        Decimal opening_balance
    }
    IncomeEntry {
        uuid income_id PK
        uuid session_id FK
        Decimal amount
        enum source_tag
        date date
    }
    CommittedCharge {
        uuid charge_id PK
        uuid session_id FK
        uuid recurring_rule_id FK
        str name
        Decimal amount
        date due_date
        enum status
    }
    RecurringRule {
        uuid rule_id PK
        uuid session_id FK
        str name
        Decimal amount
        enum frequency
        int day_of_month
        int reminder_days
    }
    FuzzyCharge {
        uuid fuzzy_id PK
        uuid session_id FK
        str name
        date due_date
        Decimal estimated_amount
        enum status
    }
    Transaction {
        uuid transaction_id PK
        uuid session_id FK
        Decimal amount
        str description
        enum category
        date date
    }

    AppSession ||--o{ IncomeEntry : "has"
    AppSession ||--o{ CommittedCharge : "has"
    AppSession ||--o{ RecurringRule : "has"
    AppSession ||--o{ FuzzyCharge : "has"
    AppSession ||--o{ Transaction : "has"
    RecurringRule ||--o{ CommittedCharge : "generates"
```

### Field reference

**AppSession**
```
session_id       uuid
start_date       date
opening_balance  Decimal
```

**IncomeEntry**
```
income_id        uuid
session_id       uuid
amount           Decimal
source_tag       enum(scholarship, family, work, other)
date             date
```

**CommittedCharge**
```
charge_id          uuid
session_id         uuid
name               str
amount             Decimal
due_date           date
status             enum(upcoming, paid)
recurring_rule_id  uuid | None
```

**RecurringRule**
```
rule_id          uuid
session_id       uuid
name             str
amount           Decimal
frequency        enum(monthly)  # Stage 1: monthly only
                               # weekly and custom deferred to Stage 2 —
                               # they require different anchor fields not modelled here
day_of_month     int            # required, range 1–31
reminder_days    int            # default 3, overridable per charge
```

> **Stage 1 constraint — monthly only:** `weekly` and `custom` frequencies need anchor fields
> that don't exist in this model (day-of-week, interval in days, explicit date list). Rather than
> ship undefined behaviour, Stage 1 locks `frequency` to `monthly` only. `day_of_month` is
> required — omitting it when using `--recurring` is a validation error. Valid range is 1–31.
> Weekly and custom are designed properly in Stage 2.

**FuzzyCharge**
```
fuzzy_id          uuid
session_id        uuid
name              str
due_date          date
estimated_amount  Decimal | None  # reference only — never used in calculations
status            enum(pending, overdue, resolved, discarded)
```

**Transaction**
```
transaction_id   uuid
session_id       uuid
amount           Decimal
description      str
category         enum(food, transport, education, entertainment, other) | None
date             date
```

---

## BalanceEngine — Calculation Contracts

All outputs are deterministic. Given the same inputs, always produces the same outputs.

### Input → output flow

```mermaid
flowchart LR
    subgraph IN[Inputs]
        I1[opening_balance]
        I2[total_income]
        I3[total_committed]
        I4[total_spent]
        I5[income_this_month]
        I6[charges_this_month]
        I7[spent_this_month]
        I8[caution_threshold]
        I9[red_threshold\ndefault 130%]
    end

    subgraph ENG[BalanceEngine]
        E1[free_money calc]
        E2[monthly_budget calc]
        E3[on_track_pct calc\nguarded — None if budget <= 0]
        E4[state classification\nno gaps]
    end

    subgraph OUT[6 Outputs]
        O1[free_money]
        O2[monthly_budget]
        O3[monthly_spent]
        O4[monthly_left]
        O5[on_track_state\ngreen / yellow / red / tight_month]
        O6[balance_state\nnormal / caution / crisis]
    end

    I1 & I2 & I3 & I4 --> E1 --> O1
    I5 & I6 --> E2 --> O2
    I7 --> O3
    E2 & I7 --> E3 --> O4
    E3 & I9 --> E4 --> O5
    O1 & I8 --> O6

    style IN fill:#f8f8f8,stroke:#ddd
    style ENG fill:#dbeafe,stroke:#1d4ed8
    style OUT fill:#dcfce7,stroke:#15803d
```

### Formulas

```python
# Free money — the core number (full session scope)
free_money = opening_balance + total_income - total_committed - total_spent

# Monthly budget — for the current calendar month
income_this_month  = sum(income entries dated this calendar month)
charges_this_month = sum(committed charges due this calendar month)
monthly_budget     = income_this_month - charges_this_month
monthly_spent      = sum(transactions dated this calendar month)
monthly_left       = monthly_budget - monthly_spent

# On-track percentage — guarded against zero/negative monthly_budget
if monthly_budget > 0:
    on_track_pct   = monthly_spent / monthly_budget * 100
else:
    on_track_pct   = None          # tight_month — no division performed

# On-track state — no gaps, no unclassified ranges
# yellow covers the full 100%–129% band (no gap between yellow and red)
# red_threshold default is 130%; yellow_threshold parameter is removed
if on_track_pct is None:
    on_track_state = tight_month   # monthly_budget <= 0; shown as a distinct state
elif on_track_pct < 100:
    on_track_state = green         # under budget
elif on_track_pct < red_threshold: # 100% up to (not including) 130% → yellow
    on_track_state = yellow
else:
    on_track_state = red           # 130% and above

# Balance state (full session scope — independent of monthly view)
balance_state  = normal   if free_money > caution_threshold
               | caution  if 0 < free_money <= caution_threshold
               | crisis   if free_money <= 0
```

> **Fix — yellow_threshold removed:** The original design had a `yellow_threshold` (110%) that
> left 110%–129% unclassified. That parameter is removed. Yellow now covers the entire range from
> 100% up to (but not including) `red_threshold` (default 130%). No gap exists.
>
> **Fix — monthly_budget ≤ 0 handled:** When `monthly_budget == 0` (charges equal income this
> month) or `monthly_budget < 0` (charges exceed income this month), `on_track_pct` is set to
> `None` and `on_track_state` becomes `tight_month`. This is a distinct state from `red` — it
> means the month's structure has no spendable budget, not that the student overspent. The
> dashboard surfaces it as: *"No spendable budget this month — charges equal or exceed expected
> income."* Overall `free_money` (full session scope) may still be positive.

### State decision tree

```mermaid
graph TD
    A{monthly_budget} --> |"> 0"| B{on_track_pct}
    A --> |"<= 0"| TM[TIGHT MONTH\nno spendable budget\ncharges >= income this month]

    B --> |"< 100%"| G[GREEN\nunder budget]
    B --> |"100% to 129%\nyellow covers full band"| Y[YELLOW\nover budget]
    B --> |">= 130%"| R[RED\nsignificantly over]

    FM{free_money} --> |"> caution_threshold"| OK[normal]
    FM --> |"0 < x <= threshold"| YB[YELLOW\nbalance caution]
    FM --> |"<= 0"| RB[RED\nbalance crisis\nshow actual negative]

    style G fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style Y fill:#fef3e2,color:#7a4f00,stroke:#c8a020
    style R fill:#fcebeb,color:#a32d2d,stroke:#a32d2d
    style TM fill:#e8e8e8,color:#333,stroke:#999
    style YB fill:#fef3e2,color:#7a4f00,stroke:#c8a020
    style RB fill:#a32d2d,color:#fff,stroke:#a32d2d
```

---

## Charge Lifecycles

### Committed charge — one-off

```mermaid
stateDiagram-v2
    direction LR
    [*] --> upcoming : charge add\ndeducts free_money immediately
    upcoming --> paid : mark-paid
    paid --> [*] : one-off complete
```

### Committed charge — recurring

```mermaid
stateDiagram-v2
    direction LR
    [*] --> upcoming : add recurring rule\nfirst occurrence created
    upcoming --> paid : mark-paid
    paid --> upcoming : next occurrence\nauto-created immediately\ndeducts free_money
    paid --> [*] : rule deleted
```

### Fuzzy charge — full lifecycle

```mermaid
stateDiagram-v2
    [*] --> pending : fuzzy-charge add\nNO deduction from free_money

    pending --> overdue : due date passes\nwithout action
    pending --> resolved : resolve with\nconfirmed amount
    pending --> discarded : discard

    overdue --> resolved : resolve with\nconfirmed amount
    overdue --> discarded : discard

    resolved --> [*] : converts to CommittedCharge\ndeducts free_money at this moment
    discarded --> [*] : no deduction ever
```

> **Invariant:** A `FuzzyCharge` in any state never affects `free_money`. Only a resolved FuzzyCharge
> that converts to a `CommittedCharge` affects the balance — and only at the moment of conversion.

---

## CLI Commands

```mermaid
mindmap
  root((CLI))
    session init
      --balance
    income add
      --amount
      --source
      --date
    charge add
      --name --amount --due-date
    charge add --recurring
      --name --amount
      --day-of-month REQUIRED
    fuzzy-charge add
      --name --due-date
      --estimate optional
    fuzzy-charge resolve
      --id --amount
    fuzzy-charge discard
      --id
    spend add
      --amount --description
      --category optional
    charge mark-paid
      --id
    dashboard show
```

| Command | Arguments | What it does |
|---|---|---|
| `session init` | `--balance` | Creates AppSession with opening balance |
| `income add` | `--amount --source --date` | Logs an IncomeEntry |
| `charge add` | `--name --amount --due-date` | Logs a one-off CommittedCharge |
| `charge add --recurring` | `--name --amount --day-of-month` | Logs a RecurringRule (monthly only). `--day-of-month` is **required** — omitting it is a validation error. Creates first occurrence immediately. |
| `fuzzy-charge add` | `--name --due-date [--estimate]` | Logs a FuzzyCharge |
| `fuzzy-charge resolve` | `--id --amount` | Resolves fuzzy charge, converts to committed |
| `fuzzy-charge discard` | `--id` | Discards fuzzy charge |
| `spend add` | `--amount --description [--category] [--date]` | Logs a Transaction |
| `charge mark-paid` | `--id` | Marks charge paid, auto-generates next occurrence if recurring |
| `dashboard show` | — | Prints free money, monthly state, on-track signal |

---

## Repository Interfaces

Defined as `typing.Protocol`. The Stage 1 adapter writes to local JSON files. Stage 3 replaces the adapter with PostgreSQL — **service code does not change**.

```mermaid
graph TD
    SVC[services.py]

    SVC --> SR[SessionRepository\nProtocol]
    SVC --> IR[IncomeRepository\nProtocol]
    SVC --> CR[ChargeRepository\nProtocol]
    SVC --> FR[FuzzyChargeRepository\nProtocol]
    SVC --> TR[TransactionRepository\nProtocol]

    SR & IR & CR & FR & TR --> A1[JSON File Adapter\nStage 1]
    A1 -.->|replaced in Stage 3| A2[PostgreSQL Adapter\nStage 3]
    A1 --> FS[(local .json files)]

    style SVC fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a
    style A1 fill:#ccfbf1,stroke:#0f766e,color:#134e4a
    style A2 fill:#f2f2f0,stroke:#ccc,color:#999
    style FS fill:#f2f2f0,stroke:#ccc,color:#666
```

```python
class SessionRepository(Protocol):
    def create(self, session: AppSession) -> None: ...
    def get_active(self) -> AppSession | None: ...

class IncomeRepository(Protocol):
    def add(self, entry: IncomeEntry) -> None: ...
    def list_for_session(self, session_id: UUID) -> list[IncomeEntry]: ...
    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[IncomeEntry]: ...

class ChargeRepository(Protocol):
    def add(self, charge: CommittedCharge) -> None: ...
    def list_upcoming(self, session_id: UUID) -> list[CommittedCharge]: ...
    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[CommittedCharge]: ...
    def mark_paid(self, charge_id: UUID) -> None: ...

class FuzzyChargeRepository(Protocol):
    def add(self, charge: FuzzyCharge) -> None: ...
    def list_pending(self, session_id: UUID) -> list[FuzzyCharge]: ...
    def update_status(self, fuzzy_id: UUID, status: FuzzyStatus) -> None: ...

class TransactionRepository(Protocol):
    def add(self, transaction: Transaction) -> None: ...
    def list_for_month(self, session_id: UUID, year: int, month: int) -> list[Transaction]: ...
```

---

## Testing Strategy

```mermaid
graph BT
    UT["Unit Tests\ntest_calculations.py\n\nFormulas · state boundaries\nedge cases · zero/negative"]
    ST["Service Tests\ntest_services.py\n\nLifecycle behaviour\nfuzzy non-deduction\nrecurring generation"]
    RT["Repository Tests\ntest_repository.py\n\nCRUD · monthly queries\npersistence across restart"]
    CT["CLI Smoke Tests\ntest_cli_flows.py\n\nHappy path end-to-end\nvalidation error paths"]

    UT --> ST --> RT --> CT

    style UT fill:#dcfce7,stroke:#15803d,color:#14532d
    style ST fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a
    style RT fill:#ccfbf1,stroke:#0f766e,color:#134e4a
    style CT fill:#fef3c7,stroke:#92400e,color:#451a03
```

### Unit — `tests/test_calculations.py`
- Free money formula with known inputs
- Monthly budget calculation (income this month minus charges this month)
- On-track percentage and state boundaries (exactly at 100%, 110%, 130%)
- Balance state boundaries (positive, zero, negative free money)
- Edge cases: no income logged yet, no charges logged yet, empty month

### Service — `tests/test_services.py`
- Recurring charge: mark-paid creates next occurrence with correct due date
- Recurring charge: next occurrence deducts from free money immediately
- Fuzzy charge: adding does not affect free money
- Fuzzy charge: resolving converts to committed charge and deducts at that moment
- Fuzzy charge: discarding does not affect free money
- FuzzyCharge and CommittedCharge remain in separate stores at all times

### Repository — `tests/test_repository.py`
- CRUD operations for all five entities
- `list_for_month` returns only entries in the correct calendar month
- Data persists correctly across a simulated restart

### CLI smoke tests — `tests/test_cli_flows.py`
- Happy path: `session init` → `income add` → `charge add` → `spend add` → `dashboard show`
- Validation error path: missing required arguments surface a clear error message
- Unknown command: surfaces a helpful usage hint

---

## Build Sequence

```mermaid
flowchart LR
    A["Phase A\nContracts\n\nEntities · protocols\nvalue objects\ntyped errors"]
    B["Phase B\nCalculations\n\nBalanceEngine\npure functions\nunit tests"]
    C["Phase C\nLifecycles\n\nRecurring\nFuzzy states\nservice tests"]
    D["Phase D\nStorage\n\nJSON adapter\nCRUD\nrepo tests"]
    E["Phase E\nCLI Wiring\n\nCommand handlers\nend-to-end\nsmoke tests"]
    F["Phase F\nQuality Gate\n\nFull test suite\nfreeze docs\nStage 2 note"]

    A --> B --> C --> D --> E --> F

    style A fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    style B fill:#dcfce7,stroke:#15803d,color:#14532d
    style C fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a
    style D fill:#ccfbf1,stroke:#0f766e,color:#134e4a
    style E fill:#fef3c7,stroke:#92400e,color:#451a03
    style F fill:#fee2e2,stroke:#b91c1c,color:#7f1d1d
```

**Phase A — Contracts**
Define entity data classes, value objects, repository protocols, and typed error classes. No implementation yet — just the shapes everything else depends on.

**Phase B — Calculations**
Implement `BalanceEngine` as pure functions. Write unit tests. Done when every formula is verified with known inputs.

**Phase C — Charge lifecycles**
Implement fuzzy charge state transitions and spend transactions in `services.py`. Base income, committed-charge creation, recurring-rule creation, and recurring next-occurrence generation are already in place; this phase completes the remaining lifecycle behavior and adds service coverage for those paths.

**Phase D — Storage**
Implement the local JSON file adapter for each repository protocol. Write repository tests. Done when data survives a simulated restart.

**Phase E — CLI wiring**
Wire all CLI commands to their service methods. Write CLI smoke tests. Done when the full happy-path flow works end-to-end from the terminal.

**Phase F — Quality gate**
Run the full test suite. Fix any failures. Freeze Stage 1 behaviour in docs. Write Stage 2 handoff note.

---

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Money precision bugs | `Decimal` enforced everywhere. `float` forbidden. Linting rule if possible. |
| Date edge-case bugs | Single `date_utils.py` module. No raw `datetime` outside it. Boundary tests at month transitions. |
| FuzzyCharge contaminating BalanceEngine | Separate repository protocol enforced architecturally. Service tests verify non-deduction. |
| Scope creep into Stage 2+ features | Explicit out-of-scope list in this document. Any addition requires updating this plan first. |
| Business logic leaking into CLI | Rule: `cli.py` contains no arithmetic, no domain decisions, no direct model mutation. |
| Division by zero in on_track_pct | `monthly_budget <= 0` check is the first operation in the on-track calculation. Returns `tight_month` state before any division is attempted. Unit test required. |
| `day_of_month` out of range | `day_of_month` validated to range 1–31. Values outside this range are rejected with a clear error at `charge add --recurring` time, not at occurrence-generation time. |

---

## Stage 2 Handoff Note

Stage 2 replaces `app/cli.py` with a CustomTkinter desktop GUI. To prepare for a clean handoff:
- All service calls must go through the existing service interfaces — the GUI calls services, never repositories directly
- All business logic stays in the service layer — no calculation or validation logic may move into the GUI layer
- The JSON storage layer remains unchanged in Stage 2 — persistence migration happens in Stage 3 (PostgreSQL)
- No Stage 3+ logic (pattern detection, reminders, history queries) may be added to Stage 1 modules, even as stubs

---

*Stage 1 — locked scope. April 2026.*
