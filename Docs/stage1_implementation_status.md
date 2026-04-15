# Stage 1 — Implementation Status
**Student Expense Tracker — CLI Core**
*Audited: 2026-04-15*

> This document is a point-in-time snapshot of what has been built, what is working,
> and what remains before Stage 1 is complete. It maps directly against the Stage 1 Implementation Plan.

---

## Overall Position

**Current phase:** End of Phase B — Calculations complete. Phase C not started.
**Test suite:** 25 / 25 passing (Phases A and B only).

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
    "Not Started (C + D + E + F)" : 4
```

```mermaid
graph LR
    A["Phase A\nContracts\n✅ COMPLETE"]:::done
    B["Phase B\nCalculations\n✅ COMPLETE"]:::done
    C["Phase C\nLifecycles\n❌ NOT STARTED"]:::todo
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

    subgraph validators["domain/validators.py ⚠️"]
        V1["parse_opening_balance ✅"]
        V2["parse_amount ❌"]
        V3["parse_income_source_tag ❌"]
        V4["parse_due_date ❌"]
        V5["parse_day_of_month ❌"]
        V6["parse_transaction_category ❌"]
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
| `parse_amount` | `domain/validators.py` | ❌ Missing |
| `parse_income_source_tag` | `domain/validators.py` | ❌ Missing |
| `parse_due_date` | `domain/validators.py` | ❌ Missing |
| `parse_day_of_month` | `domain/validators.py` | ❌ Missing |
| `parse_transaction_category` | `domain/validators.py` | ❌ Missing |
| `SessionRepository` | `ports/repositories.py` | ✅ |
| `IncomeRepository` | `ports/repositories.py` | ✅ |
| `ChargeRepository` | `ports/repositories.py` | ✅ |
| `RecurringRuleRepository` | `ports/repositories.py` | ✅ |
| `FuzzyChargeRepository` | `ports/repositories.py` | ✅ |
| `TransactionRepository` | `ports/repositories.py` | ✅ |
| Exception hierarchy | `shared/exceptions.py` | ✅ |
| `LoggerFactory` | `infrastructure/logging_config.py` | ✅ |

> **Note on validators:** `parse_opening_balance` exists. The 5 remaining validators are
> Phase C prerequisites — they must exist before any service can be written.

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

**Total: 25 / 25 tests passing.**

---

## Phase C — Charge Lifecycles `NOT STARTED`

This is the entire missing service layer. Nothing in this phase has been built.

### Services needed

```mermaid
graph TD
    subgraph existing["application/services.py — Exists"]
        SS["SessionService\ninit_session ✅"]
        BS["BalanceService\nbuild_snapshot ⚠️\n(pass-through — Phase D wires it)"]
    end

    subgraph missing["application/services.py — Missing"]
        IS["IncomeService ❌\nadd_income"]
        CS["ChargeService ❌\nadd_charge\nadd_recurring_charge\nmark_paid"]
        FS["FuzzyChargeService ❌\nadd_fuzzy_charge\nresolve\ndiscard"]
        SP["SpendService ❌\nadd_transaction"]
    end

    style SS fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style BS fill:#fef3c7,stroke:#92400e,color:#451a03
    style IS fill:#f2f2f0,stroke:#ccc,color:#999
    style CS fill:#f2f2f0,stroke:#ccc,color:#999
    style FS fill:#f2f2f0,stroke:#ccc,color:#999
    style SP fill:#f2f2f0,stroke:#ccc,color:#999
```

| Service | Method | Behaviour |
|---|---|---|
| `IncomeService` | `add_income(session_id, amount, source_tag, date)` | Validates amount > 0, creates `IncomeEntry`, persists |
| `ChargeService` | `add_charge(session_id, name, amount, due_date)` | Creates `CommittedCharge` with `status=UPCOMING`, deducts free money immediately |
| `ChargeService` | `add_recurring_charge(session_id, name, amount, day_of_month)` | Creates `RecurringRule`, generates first `CommittedCharge` occurrence immediately |
| `ChargeService` | `mark_paid(charge_id)` | Sets `status=PAID`; if `recurring_rule_id` is set, generates next occurrence automatically |
| `FuzzyChargeService` | `add_fuzzy_charge(session_id, name, due_date, estimated_amount)` | Creates `FuzzyCharge` with `status=PENDING` — **no deduction** |
| `FuzzyChargeService` | `resolve(fuzzy_id, confirmed_amount)` | Sets `status=RESOLVED`, converts to `CommittedCharge`, deducts free money at this moment |
| `FuzzyChargeService` | `discard(fuzzy_id)` | Sets `status=DISCARDED` — no deduction ever |
| `SpendService` | `add_transaction(session_id, amount, description, category, date)` | Validates amount > 0, creates `Transaction`, persists |

### Charge lifecycles to implement

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

### Service tests needed (`tests/unit/test_services.py` — file does not exist)

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
| Full test suite green | ⚠️ 25/25 pass — but only Phases A + B covered |
| `tests/unit/test_services.py` exists | ❌ |
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
        V["validators.py\n⚠️ 1 of 6 validators"]
    end

    subgraph layer_ports["Ports Layer"]
        R["repositories.py\n✅ All 6 protocols defined"]
    end

    subgraph layer_app["Application Layer"]
        C["calculations.py\n✅ Complete + tested"]
        S["services.py\n⚠️ 2 of 8 methods\nBalanceService is a pass-through"]
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
        T2["test_shared_cross_cutting.py\n✅ 3 tests"]
        T3["test_services.py\n❌ Missing"]
        T4["test_repository.py\n❌ Missing"]
        T5["test_cli_flows.py\n❌ Missing"]
    end

    style M fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style R fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style C fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style L fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style Main fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style T1 fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style T2 fill:#1a6b3c,color:#fff,stroke:#1a6b3c
    style V fill:#fef3c7,stroke:#92400e,color:#451a03
    style S fill:#fef3c7,stroke:#92400e,color:#451a03
    style J fill:#fef3c7,stroke:#92400e,color:#451a03
    style Cli fill:#fef3c7,stroke:#92400e,color:#451a03
    style T3 fill:#f2f2f0,stroke:#ccc,color:#999
    style T4 fill:#f2f2f0,stroke:#ccc,color:#999
    style T5 fill:#f2f2f0,stroke:#ccc,color:#999
```

---

## Recommended Next Steps — Phase C

Build in this order. Each step unblocks the next.

```mermaid
flowchart LR
    S1["1. Write 5 missing\nvalidators\ndomain/validators.py"]
    S2["2. IncomeService\n+ tests\nsimplest lifecycle"]
    S3["3. ChargeService\nadd_charge\none-off only first"]
    S4["4. ChargeService\nadd_recurring_charge\n+ mark_paid\nnext-occurrence logic"]
    S5["5. FuzzyChargeService\nadd / resolve / discard\nhighest-risk lifecycle"]
    S6["6. SpendService\nadd_transaction"]

    S1 --> S2 --> S3 --> S4 --> S5 --> S6

    style S1 fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    style S2 fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a
    style S3 fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a
    style S4 fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a
    style S5 fill:#fcebeb,color:#a32d2d,stroke:#a32d2d
    style S6 fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a
```

> Phase D (JSON adapters) can begin **in parallel from step 3 onwards** — service tests use
> in-memory fakes and do not depend on real adapters. Writing adapters alongside services
> keeps the two in sync and avoids a large Phase D catch-up sprint.

---

*Stage 1 — locked scope. Status as of April 2026.*
