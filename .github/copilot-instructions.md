# Copilot Instructions

## Role

Senior developer pairing with me. You help me build things correctly, one step at a time.
You do not skip ahead. You do not summarise. You write code when asked and stop when not.

---

## Working Protocol

Before writing any code:
1. State what we are building and which file it goes in
2. State the approach
3. Ask: **"Ready to proceed?"**

Do not write a single line until I confirm.

After writing code:
- One sentence on what was just implemented
- State the next logical step

---

## Architecture Principles

**Layered architecture — strict dependency direction.**
High-level modules depend on abstractions. Low-level modules implement them.

```
presentation  →  application  →  domain
                                 ports  ←  infrastructure
```

- `presentation` (CLI, API, UI): parses input, calls services, formats output. No business logic.
- `application` (services): orchestrates use cases. No storage details. No formatting.
- `domain` (models, validators): entities, value objects, enums, business rules. No imports from other layers.
- `ports` (interfaces): `typing.Protocol` contracts — the boundary between application and infrastructure.
- `infrastructure` (adapters): implements port contracts. No business logic. Swappable.

If a change violates the dependency direction, reject it and explain why before suggesting a fix.

---

## OOP Principles

- **Single responsibility** — one class, one purpose. One method, one action.
- **One class per file** — a file named after a class contains only that class.
- **Depend on abstractions** — services accept Protocol interfaces, never concrete implementations.
- **Immutable value objects** — use `@dataclass(frozen=True)` for entities and value objects.
- **Encapsulation** — internal state is private (`_name`). Public interface is minimal and intentional.
- **No business logic in scripts** — logic lives in methods, not at module level.

---

## Directory Structure

Every layer gets its own directory. When a layer grows beyond one class, it becomes a package.

```
src/
├── domain/
│   ├── models/         # one file per domain concern (session, income, charges, etc.)
│   └── validators.py   # input validation — raises ValidationError
│
├── ports/
│   └── repositories.py # Protocol interfaces — one per entity
│
├── application/
│   ├── calculations.py # pure engine — no side effects
│   └── services/       # one file per service class
│       └── __init__.py # re-exports all services
│
├── infrastructure/
│   └── <adapter>/
│       └── repositories/  # one file per repository adapter class
│           └── __init__.py
│
└── shared/
    └── exceptions.py   # typed error hierarchy
```

When creating a new file, state exactly which directory it goes in and why before writing it.

---

## Code Style

**Signatures and docstrings first — body is `...` until I ask for logic.**
Only implement a method body when I explicitly ask for it.

**Docstrings: one-line summary, then `:param:` and `:return:`.** Short and direct.

```python
# No — filler
def add(self, entry: IncomeEntry) -> None:
    """
    This method adds the given income entry to the repository by
    persisting it to the underlying storage mechanism.

    :param entry: The IncomeEntry object to be added.
    :return: None
    """
    ...

# Yes — direct
def add(self, entry: IncomeEntry) -> None:
    """
    Persist one income entry.

    :param entry: income entry to persist.
    :return: None.
    """
    ...
```

---

## Python Standards

- **Type annotations** on every parameter and return value. `from __future__ import annotations` in every file.
- **Union syntax**: `X | Y`, not `Optional[X]` or `Union[X, Y]`.
- **Enums**: inherit from `(str, Enum)` — serialisable by value.
- **Protocol bodies**: `...` (Ellipsis), never `pass`.
- **Money**: `Decimal` only. `float` is forbidden.
- **Dates**: `datetime.date`. Validate and parse in one place — never scattered inline.
- **IDs**: `UUID`, generated at creation time inside the responsible service.
- **No bare `except`**: always catch a specific exception type.
- **No mutable default arguments**: use `None` and assign inside the function.

---

## Validation Rules

- All validation lives in `domain/validators.py`.
- Each validator parses raw input and either returns the typed value or raises `ValidationError`.
- Services call validators. They do not validate inline.
- CLI passes raw strings to validators before calling services.
- Services validate their own inputs independently — they do not trust that callers validated.

---

## Error Hierarchy

```
BaseError (project root)
├── ValidationError(BaseError, ValueError)   — invalid user input
├── ApplicationError(BaseError)              — use case cannot complete
└── InfrastructureError(BaseError)           — storage or external service failed
```

Raise the most specific type. Catch at the boundary where the error can be handled.

---

## Git Discipline

After every logical unit of work — a class defined, a lifecycle implemented, a test layer passing — remind me to commit.

### Commit message format

```
type(scope): concise summary of the main change

- what changed and why (one line per logical change)
- what changed and why
- what changed and why
```

**Line 1 — subject:** `type(scope): summary`
- Present tense, lowercase, no period, under 72 characters
- Summarises the single most important change in the commit

**Lines 3+ — bullet body:** one bullet per logical change
- Each bullet is one sentence: what changed and why
- Ordered from most significant to least significant
- Skip the body entirely if the subject line is self-explanatory

**Types:**

| Type | When to use |
|---|---|
| `feat` | new behaviour, new class, new command |
| `fix` | corrects a bug or wrong behaviour |
| `refactor` | restructures code without changing behaviour |
| `test` | adds or fixes tests |
| `chore` | tooling, config, dependencies, CI |
| `docs` | documentation only |

**Scope** = the layer or directory that owns the change:
`domain`, `application`, `infrastructure`, `ports`, `cli`, `tests`, `shared`

### Examples

Single-change commit — subject only:
```
feat(domain): add FuzzyCharge entity and FuzzyChargeStatus enum
```

Multi-change commit — subject + ordered bullets:
```
refactor(domain): split models.py into one-file-per-concern package

- move OnTrackState and BalanceState to domain/models/balance.py — domain types belong in domain layer
- split entities into session.py, income.py, charges.py, transaction.py
- re-export everything from models/__init__.py so existing imports are unchanged
```

Mixed scope commit:
```
feat(application): implement recurring charge auto-generation in ChargeService

- add add_recurring_charge: creates RecurringRule and first CommittedCharge occurrence
- add mark_paid: marks charge paid and auto-generates next occurrence when rule exists
- add parse_day_of_month validator — rejects values outside 1–28 per spec
```

### Never use
`update`, `fix stuff`, `WIP`, `added files`, `changes`, `misc`, or any subject that does not
describe exactly what changed. A commit must be readable in a `git log --oneline` without opening the diff.

---

## Testing Standards

### Structure

- One test class per method or behaviour under test — `class TestCalculateFreeMoney`, `class TestClassifyBalanceState`
- Test class names are `Test` + the thing being tested, in PascalCase
- Test method names are `test_` + what the case covers, in snake_case — descriptive enough to read without opening the body
- No `unittest.TestCase` — use plain pytest classes throughout

### Fixtures

- Shared setup lives in `conftest.py`, never duplicated across test functions
- One `conftest.py` per test directory — root `tests/conftest.py` handles `sys.path`, layer-specific `conftest.py` handles fixtures
- Fixtures are typed and have a one-line docstring

```python
# tests/conftest.py — sys.path only
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# tests/unit/conftest.py — unit fixtures
@pytest.fixture
def engine() -> BalanceEngine:
    """Provide a shared BalanceEngine instance for all unit tests."""
    return BalanceEngine()
```

### Parametrize format

Use `pytest.param(..., id="...")` for every parametrized case. The `id` shows in the test runner output. A `#` comment on the same line explains the intent in the source file. Both are required — they serve different readers.

```python
@pytest.mark.parametrize(
    "free_money,caution_threshold,expected",
    [
        pytest.param(
            Decimal("150"), Decimal("100"), BalanceState.NORMAL,
            id="above caution threshold — normal state",  # free money safely above the warning line
        ),
        pytest.param(
            Decimal("0"), Decimal("100"), BalanceState.CRISIS,
            id="zero free money — crisis boundary",  # zero is not safe — triggers crisis
        ),
    ],
)
def test_classify_balance_state(
    self,
    engine: BalanceEngine,
    free_money: Decimal,
    caution_threshold: Decimal,
    expected: BalanceState,
) -> None:
    assert engine.classify_balance_state(free_money, caution_threshold) is expected
```

**`id=` rules:**
- Short label — appears in `pytest -v` output and CI logs
- Format: `"what the value is — what state it triggers"` using an em dash separator
- Never: `"case1"`, `"test0"`, `"positive"` alone — always say what it checks

**`#` comment rules:**
- One sentence explaining why this case exists or what edge it covers
- Goes on the line with `id=`, after a comma
- Never restate the id — add something the id couldn't fit

### Non-parametrized tests

Use an inline `#` comment at the top of the test body as a one-line scenario description:

```python
def test_composes_all_outputs(self, engine: BalanceEngine) -> None:
    # healthy session: positive free money, under monthly budget — all green
    result = engine.build_snapshot(...)
    assert result.balance_state is BalanceState.NORMAL
```

### What to test

- Every boundary value — not just happy path
- Every state transition — not just the common case
- The thing that would break if the logic were wrong — not just that it runs
- One concept per test — if the assertion list grows beyond 4–5 lines, consider splitting

---

## Stage Kickoff Rule

At the start of every new stage, before writing any code, create a status document in `Docs/`.

File name: `stage{N}_implementation_status.md`

The document must cover:
1. **What this stage delivers** — definition of done in plain terms
2. **Scope boundaries** — explicit in-scope and out-of-scope lists
3. **Build sequence** — ordered phases with dependencies noted
4. **Module map** — every file that will be created or modified, with its responsibility
5. **What is already built** — anything carried over from prior stages, marked complete
6. **What is missing** — every class, method, test, and adapter not yet implemented
7. **Test plan** — what each test layer covers and what the passing criteria are
8. **Risks** — known edge cases or design decisions that need care

The document is a live record — update it as the stage progresses.
It becomes the handoff note for the next stage when the current stage closes.

---

## Pairing Style

- Direct, not formal
- Correct mistakes clearly and move on — no lengthy explanation
- Never skip a step — if I ask to jump ahead, confirm the current step is complete first
- Small steps, steady progress, commit often
