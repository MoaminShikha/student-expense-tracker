# Stage 1 — Implementation Status
**Student Expense Tracker — CLI Core**
*Audited: 2026-04-15*

> This document is a point-in-time snapshot of what has been built, what is working,
> and what remains before Stage 1 is complete. It maps directly against the Stage 1 Implementation Plan.

---

## Overall Position

**Current phase:** Mid Phase C — core service lifecycles in progress.
**Test suite:** 101 / 101 passing (unit suite).

```mermaid
gantt
    title Stage 1 Build Sequence — Progress
    dateFormat X
    axisFormat %s

    section Phase A — Contracts
    Entities · Protocols · Errors   :done, a1, 0, 1

    section Phase B — Calculations
    BalanceEngine · Unit Tests      :done, b1, 1, 2

    section Phase C — Lifecycles
    Services · Validators · Service Tests :active, c1, 2, 3

    section Phase D — Storage
    JSON Adapters · Repo Tests      :c1, 3, 4

    section Phase E — CLI Wiring
    Command Handlers · Smoke Tests  :c1, 4, 5

    section Phase F — Quality Gate
    Full Suite · Freeze Docs        :c1, 5, 6
```

---

## Phase Progress — At a Glance

```mermaid
pie title Phases Complete vs Remaining
    "Complete (A + B)" : 2
    "In Progress (C)" : 1
    "Not Started (D + E + F)" : 3
```

```mermaid
graph LR
    A["Phase A\nContracts\n✅ COMPLETE"]:::done
    B["Phase B\nCalculations\n✅ COMPLETE"]:::done
    C["Phase C\nLifecycles\n⚙️ IN PROGRESS"]:::partial
    D["Phase D\nStorage\n❌ NOT STARTED"]:::todo
    E["Phase E\nCLI Wiring\n⚠️ 1 of 10 commands"]:::partial
    F["Phase F\nQuality Gate\n❌ NOT STARTED"]:::todo

    A --> B --> C --> D --> E --> F

    classDef done fill:#1a6b3c,stroke:#1a6b3c,color:#fff
    classDef todo fill:#f2f2f0,stroke:#ccc,color:#999
    classDef partial fill:#fef3c7,stroke:#92400e,color:#451a03
```

---

## Phase A — Contracts `COMPLETE`

All domain entities, value objects, repository protocols, and typed errors are in place.

```mermaid
graph TD
    subgraph models["domain/models.py ✅"]
        AppSession
        IncomeEntry
        CommittedCharge
        RecurringRule
        FuzzyCharge
        Transaction
        Enums["Enums\nIncomeSourceTag\nChargeStatus\nRecurringFrequency\nFuzzyChargeStatus\nTransactionCategory"]
    end

    subgraph protocols["ports/repositories.py ✅"]
        SR[SessionRepository]
        IR[IncomeRepository]
        CR[ChargeRepository]
        RR[RecurringRuleRepository]
        FR[FuzzyChargeRepository]
        TR[TransactionRepository]
    end

    subgraph shared["shared/ ✅"]
        ExpenseTrackerError
        ValidationError
        ApplicationError
        InfrastructureError
        LoggingConfigurationError
    end

    subgraph validators["domain/validators.py ✅"]
        V1["parse_opening_balance ✅"]
        V2["parse_amount ✅"]
        V3["parse_income_source_tag ✅"]
        V4["parse_due_date ✅"]
        V5["parse_day_of_month ✅"]
        V6["parse_transaction_category ✅"]
    end
```

| Artifact | File | Status |
|---|---|---|
| `AppSession` | `domain/models.py` | ✅ |
| `IncomeEntry` | `domain/models.py` | ✅ |
| `CommittedCharge` | `domain/models.py` | ✅ |
| `RecurringRule` | `domain/models.py` | ✅ |
| `FuzzyCharge` | `domain/models.py` | ✅ |
| `Transaction` | `domain/models.py` | ✅ |
| All enums | `domain/models.py` | ✅ |
| `parse_opening_balance` | `domain/validators.py` | ✅ |
| `parse_amount` | `domain/validators.py` | ✅ |
| `parse_income_source_tag` | `domain/validators.py` | ✅ |
| `parse_due_date` | `domain/validators.py` | ✅ |
| `parse_day_of_month` | `domain/validators.py` | ✅ |
| `parse_transaction_category` | `domain/validators.py` | ✅ |
| `SessionRepository` | `ports/repositories.py` | ✅ |
| `IncomeRepository` | `ports/repositories.py` | ✅ |
| `ChargeRepository` | `ports/repositories.py` | ✅ |
| `RecurringRuleRepository` | `ports/repositories.py` | ✅ |
| `FuzzyChargeRepository` | `ports/repositories.py` | ✅ |
| `TransactionRepository` | `ports/repositories.py` | ✅ |
| Exception hierarchy | `shared/exceptions.py` | ✅ |
| `LoggerFactory` | `infrastructure/logging_config.py` | ✅ |

> **Note on validators:** all Stage 1 validator functions are now implemented and covered by
> `tests/unit/test_validators.py`.

---

## Phase B — Calculations `COMPLETE`

`BalanceEngine` is pure, deterministic, and fully tested at all spec boundaries.

```mermaid
graph LR
    subgraph inputs[Inputs]
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

    subgraph engine["BalanceEngine ✅"]
        E1["calculate_free_money ✅"]
        E2["calculate_monthly_budget ✅"]
        E3["classify_on_track_state ✅"]
        E4["classify_balance_state ✅"]
        E5["build_snapshot ✅"]
    end

    subgraph outputs[Outputs]
        O1[free_money]
        O2[monthly_budget]
        O3[monthly_spent]
        O4[monthly_left]
        O5[on_track_state\nGREEN/YELLOW/RED/TIGHT_MONTH]
        O6[balance_state\nNORMAL/CAUTION/CRISIS]
    end

    I1 & I2 & I3 & I4 --> E1 --> O1
    I5 & I6 & I7 --> E2 --> O2 & O3 & O4
    E2 & I9 --> E3 --> O5
    O1 & I8 --> E4 --> O6
    E1 & E2 & E3 & E4 --> E5

    style E1 fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style E2 fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style E3 fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style E4 fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style E5 fill:#1a6b3c,color:#fff,stroke:#1a6b3c
```

| Artifact | File | Status |
|---|---|---|
| `BalanceEngine.calculate_free_money` | `application/calculations.py` | ✅ |
| `BalanceEngine.calculate_monthly_budget` | `application/calculations.py` | ✅ |
| `BalanceEngine.classify_on_track_state` | `application/calculations.py` | ✅ |
| `BalanceEngine.classify_balance_state` | `application/calculations.py` | ✅ |
| `BalanceEngine.build_snapshot` | `application/calculations.py` | ✅ |
| `MonthlyBudgetView` output type | `application/calculations.py` | ✅ |
| `BalanceSnapshot` output type | `application/calculations.py` | ✅ |
| Unit tests — free money (4 cases) | `tests/unit/test_calculations.py` | ✅ |
| Unit tests — balance state (5 boundary cases) | `tests/unit/test_calculations.py` | ✅ |
| Unit tests — on-track state (7 boundary cases) | `tests/unit/test_calculations.py` | ✅ |
| Unit tests — monthly budget (4 cases) | `tests/unit/test_calculations.py` | ✅ |
| Unit tests — snapshot composition (2 cases) | `tests/unit/test_calculations.py` | ✅ |
| Cross-cutting tests — exceptions + logging | `tests/unit/test_shared_cross_cutting.py` | ✅ |

**Total: calculations remain fully green; full unit suite now passes 84 / 84.**

---

## Phase C — Charge Lifecycles `IN PROGRESS`

Core service wiring has started. Income and committed-charge base lifecycles are implemented; recurring, fuzzy, and spend lifecycles remain.

### Services needed

```mermaid
graph TD
    subgraph existing["application/services/ — Implemented"]
        SS["SessionService\ninit_session ✅"]
        BS["BalanceService\nbuild_snapshot ⚠️\n(pass-through — Phase D wires it)"]
        IS["IncomeService\nadd_income ✅"]
        CS1["ChargeService\nadd_charge ✅\nadd_recurring_charge ✅\nmark_paid recurring ✅"]
    end

    subgraph missing["application/services/ — Remaining"]
        CS["ChargeService ⚠️\nremaining: fuzzy + spend"]
        FS["FuzzyChargeService ❌\nadd_fuzzy_charge\nresolve\ndiscard"]
        SP["SpendService ❌\nadd_transaction"]
    end

    style SS fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style BS fill:#fef3c7,stroke:#92400e,color:#451a03
    style IS fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style CS1 fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style CS fill:#fef3c7,stroke:#92400e,color:#451a03
    style FS fill:#f2f2f0,stroke:#ccc,color:#999
    style SP fill:#f2f2f0,stroke:#ccc,color:#999
```

| Service | Method | Behaviour |
|---|---|---|
| `IncomeService` | `add_income(amount, source_tag, entry_date)` | ✅ Implemented — validates input, creates `IncomeEntry`, persists for active session |
| `ChargeService` | `add_charge(name, amount, due_date)` | ✅ Implemented — creates `CommittedCharge` with `status=UPCOMING` for active session |
| `ChargeService` | `add_recurring_charge(name, amount, day_of_month)` | ✅ Implemented — creates `RecurringRule` and first `CommittedCharge` occurrence |
| `ChargeService` | `mark_paid(charge_id)` | ✅ Implemented — marks paid and creates the next recurring occurrence when linked to a rule |
| `FuzzyChargeService` | `add_fuzzy_charge(session_id, name, due_date, estimated_amount)` | Creates `FuzzyCharge` with `status=PENDING` — **no deduction** |
| `FuzzyChargeService` | `resolve(fuzzy_id, confirmed_amount)` | Sets `status=RESOLVED`, converts to `CommittedCharge`, deducts free money at this moment |
| `FuzzyChargeService` | `discard(fuzzy_id)` | Sets `status=DISCARDED` — no deduction ever |
| `SpendService` | `add_transaction(session_id, amount, description, category, date)` | Validates amount > 0, creates `Transaction`, persists |

### Charge lifecycles remaining

```mermaid
stateDiagram-v2
    direction LR
    note right of upcoming : One-off lifecycle
    [*] --> upcoming : add_charge\ndeducts free_money immediately
    upcoming --> paid : mark_paid
    paid --> [*]
```

```mermaid
stateDiagram-v2
    direction LR
    note right of upcoming : Recurring lifecycle
    [*] --> upcoming : add_recurring_charge\nfirst occurrence created
    upcoming --> paid : mark_paid
    paid --> upcoming : next occurrence\nauto-created immediately
    paid --> [*] : rule deleted
```

```mermaid
stateDiagram-v2
    note right of pending : Fuzzy lifecycle — never touches free_money directly
    [*] --> pending : add_fuzzy_charge\nNO deduction
    pending --> overdue : due date passes
    pending --> resolved : resolve with confirmed amount
    pending --> discarded : discard
    overdue --> resolved : resolve with confirmed amount
    overdue --> discarded : discard
    resolved --> [*] : converts to CommittedCharge\ndeducts free_money HERE
    discarded --> [*] : no deduction ever
```

### Service tests status

Implemented files:
- `tests/unit/test_income_service.py`
- `tests/unit/test_charge_service.py`

Still needed for remaining Phase C behavior:

| Test | What it verifies |
|---|---|
| Recurring `mark_paid` creates next occurrence | Correct `due_date` generated from `day_of_month` |
| Next occurrence deducts free money immediately | Balance decreases at generation time |
| Fuzzy `add_fuzzy_charge` does not affect free money | Core invariant from design file |
| Fuzzy `resolve` converts and deducts at that moment | `CommittedCharge` created, free money drops |
| Fuzzy `discard` makes no deduction | Free money unchanged |
| FuzzyCharge and CommittedCharge stay in separate stores | Never mixed across repos |

---

## Phase D — Storage `NOT STARTED`

The JSON adapter file exists but every method body is `pass` — nothing is implemented.

```mermaid
graph TD
    subgraph adapters["infrastructure/json/repositories.py"]
        JSR["JsonSessionRepository\n⚠️ Stub — pass bodies"]
        JIR["JsonIncomeRepository\n❌ Missing"]
        JCR["JsonChargeRepository\n❌ Missing"]
        JRR["JsonRecurringRuleRepository\n❌ Missing"]
        JFR["JsonFuzzyChargeRepository\n❌ Missing"]
        JTR["JsonTransactionRepository\n❌ Missing"]
    end

    subgraph protocols["ports/repositories.py ✅"]
        SR[SessionRepository]
        IR[IncomeRepository]
        CR[ChargeRepository]
        RR[RecurringRuleRepository]
        FR[FuzzyChargeRepository]
        TR[TransactionRepository]
    end

    JSR -.->|implements| SR
    JIR -.->|implements| IR
    JCR -.->|implements| CR
    JRR -.->|implements| RR
    JFR -.->|implements| FR
    JTR -.->|implements| TR

    style JSR fill:#fef3c7,stroke:#92400e,color:#451a03
    style JIR fill:#f2f2f0,stroke:#ccc,color:#999
    style JCR fill:#f2f2f0,stroke:#ccc,color:#999
    style JRR fill:#f2f2f0,stroke:#ccc,color:#999
    style JFR fill:#f2f2f0,stroke:#ccc,color:#999
    style JTR fill:#f2f2f0,stroke:#ccc,color:#999
```

| Adapter | Status | Notes |
|---|---|---|
| `JsonSessionRepository` | ⚠️ Stub | Class exists, all methods are `pass` |
| `JsonIncomeRepository` | ❌ Missing | Class does not exist |
| `JsonChargeRepository` | ❌ Missing | Class does not exist |
| `JsonRecurringRuleRepository` | ❌ Missing | Class does not exist |
| `JsonFuzzyChargeRepository` | ❌ Missing | Class does not exist |
| `JsonTransactionRepository` | ❌ Missing | Class does not exist |
| Repository tests | ❌ Missing | `tests/unit/test_repository.py` does not exist |

**Serialisation rules** that each adapter must follow (per design contracts):
- `Decimal` → stored as `str` (never `float`)
- `date` → stored as ISO 8601 string (`YYYY-MM-DD`)
- `UUID` → stored as `str`
- `Enum` → stored as `.value`

**Repository test requirements** (per spec):
- CRUD operations for all five entity types
- `list_for_month` returns only entries in the correct calendar month
- Data persists correctly across a simulated restart (write → re-instantiate adapter → read back)

---

## Phase E — CLI Wiring `1 of 10 commands`

```mermaid
graph TD
    CLI[CliApplication]

    CLI --> SI["session init\n✅ WIRED"]
    CLI --> IA["income add\n❌ Missing"]
    CLI --> CA["charge add\n❌ Missing"]
    CLI --> CAR["charge add --recurring\n❌ Missing"]
    CLI --> FCA["fuzzy-charge add\n❌ Missing"]
    CLI --> FCR["fuzzy-charge resolve\n❌ Missing"]
    CLI --> FCD["fuzzy-charge discard\n❌ Missing"]
    CLI --> SA["spend add\n❌ Missing"]
    CLI --> CMP["charge mark-paid\n❌ Missing"]
    CLI --> DS["dashboard show\n⚠️ Scaffold only\nPhase D dependency"]

    style SI fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style DS fill:#fef3c7,stroke:#92400e,color:#451a03
    style IA fill:#f2f2f0,stroke:#ccc,color:#999
    style CA fill:#f2f2f0,stroke:#ccc,color:#999
    style CAR fill:#f2f2f0,stroke:#ccc,color:#999
    style FCA fill:#f2f2f0,stroke:#ccc,color:#999
    style FCR fill:#f2f2f0,stroke:#ccc,color:#999
    style FCD fill:#f2f2f0,stroke:#ccc,color:#999
    style SA fill:#f2f2f0,stroke:#ccc,color:#999
    style CMP fill:#f2f2f0,stroke:#ccc,color:#999
```

| Command | Arguments | Handler | Status |
|---|---|---|---|
| `session init` | `--balance` | `handle_session_init` | ✅ |
| `income add` | `--amount --source --date` | — | ❌ |
| `charge add` | `--name --amount --due-date` | — | ❌ |
| `charge add --recurring` | `--name --amount --day-of-month` | — | ❌ |
| `fuzzy-charge add` | `--name --due-date [--estimate]` | — | ❌ |
| `fuzzy-charge resolve` | `--id --amount` | — | ❌ |
| `fuzzy-charge discard` | `--id` | — | ❌ |
| `spend add` | `--amount --description [--category] [--date]` | — | ❌ |
| `charge mark-paid` | `--id` | — | ❌ |
| `dashboard show` | *(no arguments)* | `handle_dashboard_show` | ⚠️ Scaffold |

> **`dashboard show` note:** The handler correctly accepts no arguments and rejects any that are
> passed. It returns a Phase D not-yet-implemented error until the repository layer is wired and
> a `DashboardService` aggregates totals from all repositories.

**CLI smoke tests** (`tests/unit/test_cli_flows.py`) — file does not exist yet.

---

## Phase F — Quality Gate `NOT STARTED`

| Item | Status |
|---|---|
| Full test suite green | ✅ 101/101 unit tests pass |
| Service tests for implemented methods | ✅ `test_income_service.py`, `test_charge_service.py` |
| `tests/unit/test_repository.py` exists | ❌ |
| `tests/unit/test_cli_flows.py` exists | ❌ |
| Stage 1 behaviour frozen in docs | ❌ |
| Stage 2 handoff note written | ❌ |

---

## Layer-by-Layer Summary

```mermaid
graph TD
    subgraph layer_domain["Domain Layer"]
        M["models.py\n✅ Complete"]
        V["validators.py\n✅ 6 of 6 validators"]
    end

    subgraph layer_ports["Ports Layer"]
        R["repositories.py\n✅ All 6 protocols defined"]
    end

    subgraph layer_app["Application Layer"]
        C["calculations.py\n✅ Complete + tested"]
        S["services/\n⚠️ In progress\nSession + Income + Charge(base + recurring) implemented"]
    end

    subgraph layer_infra["Infrastructure Layer"]
        J["json/repositories.py\n⚠️ 1 stub, 5 missing\n0 methods implemented"]
        L["logging_config.py\n✅ Complete"]
    end

    subgraph layer_cli["CLI Layer"]
        Main["main.py\n✅ Bootstraps correctly"]
        Cli["cli.py\n⚠️ 1 of 10 commands"]
    end

    subgraph layer_tests["Tests"]
        T1["test_calculations.py\n✅ 22 tests"]
        T2["test_shared_cross_cutting.py\n✅ 8 tests"]
        T3["test_validators.py\n✅ 50 tests"]
        T4["test_income_service.py\n✅ 4 tests"]
        T5["test_charge_service.py\n✅ 22 tests"]
        T6["test_repository.py\n❌ Missing"]
        T7["test_cli_flows.py\n❌ Missing"]
    end

    style M fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style R fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style C fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style L fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style Main fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style T1 fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style T2 fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style V fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style S fill:#fef3c7,stroke:#92400e,color:#451a03
    style J fill:#fef3c7,stroke:#92400e,color:#451a03
    style Cli fill:#fef3c7,stroke:#92400e,color:#451a03
    style T3 fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style T4 fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style T5 fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style T6 fill:#f2f2f0,stroke:#ccc,color:#999
    style T7 fill:#f2f2f0,stroke:#ccc,color:#999
```

---

## Recommended Next Steps — Phase C

Build in this order. Each step unblocks the next.

```mermaid
flowchart LR
    S1["1. FuzzyChargeService\nadd / resolve / discard\nkeep no-deduction invariant"]
    S2["2. SpendService\nadd_transaction"]
    S3["3. Begin Phase D\nJSON repositories\nstart with session + income + charge"]
    S4["4. CLI wiring\nmap implemented services\nto command handlers"]
    S5["5. Full unit + smoke gate\nthen freeze Stage 1 docs"]
    S6["6. Stage 2 handoff\nlock final scope"]

    S1 --> S2 --> S3 --> S4 --> S5 --> S6

    style S1 fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a
    style S2 fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a
    style S3 fill:#ccfbf1,stroke:#0f766e,color:#134e4a
    style S4 fill:#fef3c7,stroke:#92400e,color:#451a03
    style S5 fill:#fcebeb,color:#a32d2d,stroke:#a32d2d
    style S6 fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
```

> Phase D (JSON adapters) can begin **in parallel from step 3 onwards** — service tests use
> in-memory fakes and do not depend on real adapters. Writing adapters alongside services
> keeps the two in sync and avoids a large Phase D catch-up sprint.

---

*Stage 1 — locked scope. Status as of April 2026.*
