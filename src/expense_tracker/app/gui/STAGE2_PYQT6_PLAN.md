# Stage 2 PyQt6 Plan

## Purpose

Stage 2 adds a native PyQt6 desktop dashboard for the existing Student Expense Tracker.

This is a new presentation layer only. It must call the existing application services and keep the Stage 1 domain, calculations, repository protocols, and JSON adapters unchanged.

## Current Baseline

Stage 1 provides:

- Domain models for sessions, income, charges, fuzzy charges, transactions, and balance snapshots.
- Pure balance calculations through `BalanceEngine`.
- Services for session, income, charges, fuzzy charges, spending, and dashboard snapshots.
- JSON repositories implementing the repository protocols.
- CLI command routing for every core workflow.
- HTML dashboard mockups in `Docs/visuals/`, especially `mizan_dashboard.html`.

Before starting GUI implementation, fix the known entrypoint issue in `app/main.py` by importing `Decimal`.

## Architecture Rule

The GUI follows the same dependency direction as the CLI:

```text
gui views/dialogs -> gui controllers/view models -> application services -> ports -> infrastructure/json
```

The GUI must not:

- Calculate free money itself.
- Read or write JSON files directly.
- Create domain objects when a service method already owns that workflow.
- Move validation, business rules, or balance logic out of the service/application layer.

## Directory Roles

```text
gui/
  controllers/   Coordinates user actions and service calls.
  dialogs/       Modal forms for add income, add spend, add charge, fuzzy flows.
  resources/     Static GUI assets when needed.
  styles/        Qt stylesheet files and visual tokens.
  view_models/   UI-shaped read models derived from domain/service outputs.
  views/         Main windows and screen-level widgets.
  widgets/       Reusable small widgets such as money cards and status pills.
```

## PyQt6 Learning Path

Build the GUI in the same order the concepts are needed:

1. `QApplication` and `QMainWindow`
2. `QWidget` composition
3. `QVBoxLayout`, `QHBoxLayout`, and `QGridLayout`
4. `QLabel`, `QPushButton`, `QLineEdit`, `QComboBox`, `QDateEdit`
5. Signals and slots with `.clicked.connect(...)`
6. Dialogs with `QDialog`
7. Refreshing the dashboard after service writes
8. Qt stylesheets for the Mizān visual language

## Milestone 1: Real Dashboard Window

Goal: open a native window that shows real data from the existing JSON-backed services.

Deliverables:

- GUI entrypoint under `app/gui/`.
- Bootstrap function that creates the same repositories and services as the CLI.
- Main dashboard window.
- Empty-state handling when no session exists.
- Real `BalanceSnapshot` display when a session exists.

Dashboard data:

- Free money
- Monthly budget
- Monthly spent
- Monthly left
- On-track state
- Balance state

## Milestone 2: Add Spend Loop

Goal: prove the full GUI write loop works.

Deliverables:

- `AddSpendDialog`
- Amount input
- Description input
- Optional category selector
- Optional date input defaulting to today
- Service call to `SpendService.add_transaction(...)`
- Dashboard refresh after successful save
- Error dialog for validation/application failures

This milestone teaches the complete pattern used by every later form.

## Milestone 3: Core Money Forms

Goal: make the Stage 1 workflows usable without the terminal.

Deliverables:

- `SessionInitDialog`
- `AddIncomeDialog`
- `AddChargeDialog`
- `AddRecurringChargeDialog`
- `MarkPaidDialog` or mark-paid button in the upcoming charges list

Each dialog calls the matching existing service method.

## Milestone 4: Lists

Goal: make the dashboard useful as a daily app.

Deliverables:

- Upcoming charges panel
- Recent transactions panel
- Basic category spending panel
- Refresh action

Use repository/service data through a controller or view model. Do not query JSON files from widgets.

## Milestone 5: Fuzzy Charges

Goal: surface uncertain charges cleanly.

Deliverables:

- Pending fuzzy entries list
- Add fuzzy charge dialog
- Resolve fuzzy charge dialog
- Discard fuzzy charge action

Fuzzy entries never affect free money until resolved, matching the Stage 1 invariant.

## Milestone 6: Visual Polish

Goal: bring the PyQt6 app closer to the Mizān dashboard mockup.

Deliverables:

- Status colors for normal, caution, crisis
- On-track colors for green, yellow, red, tight month
- Money card styling
- Sidebar or top navigation
- Consistent spacing and typography
- Qt stylesheet extracted under `styles/`

Do this after the app is usable.

## Out Of Scope For Stage 2

- PostgreSQL
- FastAPI or React
- Bank connectivity
- Pattern detection
- Real reminder scheduler
- Authentication
- Multi-user support
- Rewriting existing services
- Replacing the CLI

## Definition Of Done

Stage 2 is complete when:

- The app opens directly to a native dashboard window.
- A student can initialize a session from the GUI.
- A student can add income, charges, recurring charges, fuzzy charges, and spend from the GUI.
- A student can mark charges paid and resolve or discard fuzzy charges.
- The dashboard refreshes after every write.
- The CLI still works.
- Existing Stage 1 tests still pass.
