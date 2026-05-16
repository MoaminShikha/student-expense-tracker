from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

from PyQt6.QtWidgets import QApplication

_HERE         = Path(__file__).resolve()
_SRC_DIR      = _HERE.parents[3]
_PROJECT_ROOT = _SRC_DIR.parent
_DATA_DIR     = _PROJECT_ROOT / "data"

if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from expense_tracker.application.calculations import BalanceEngine
from expense_tracker.application.services import (
    BalanceService,
    ChargeService,
    FuzzyChargeService,
    IncomeService,
    SessionService,
    SpendService,
)
from expense_tracker.infrastructure.json.repositories import (
    JsonChargeRepository,
    JsonFuzzyChargeRepository,
    JsonIncomeRepository,
    JsonRecurringRuleRepository,
    JsonSessionRepository,
    JsonTransactionRepository,
)
from expense_tracker.app.gui.styles.fonts import load_fonts
from expense_tracker.app.gui.controllers.activity_controller import ActivityController
from expense_tracker.app.gui.controllers.dashboard_controller import DashboardController
from expense_tracker.app.gui.controllers.insights_controller import InsightsController
from expense_tracker.app.gui.views.main_window import MainWindow

_CAUTION_THRESHOLD = Decimal("100")


def main() -> int:
    app = QApplication([])
    load_fonts()

    try:
        session_repo = JsonSessionRepository(_DATA_DIR / "session.json")
        income_repo  = JsonIncomeRepository(_DATA_DIR / "income.json")
        charge_repo  = JsonChargeRepository(_DATA_DIR / "charges.json")
        rule_repo    = JsonRecurringRuleRepository(_DATA_DIR / "recurring_rules.json")
        fuzzy_repo   = JsonFuzzyChargeRepository(_DATA_DIR / "fuzzy_charges.json")
        tx_repo      = JsonTransactionRepository(_DATA_DIR / "transactions.json")

        engine              = BalanceEngine()
        session_service     = SessionService(session_repo)
        income_service      = IncomeService(session_repo, income_repo)
        charge_service      = ChargeService(session_repo, charge_repo, rule_repo)
        fuzzy_charge_service = FuzzyChargeService(session_repo, fuzzy_repo, charge_repo, income_repo)
        spend_service       = SpendService(session_repo, tx_repo)
        balance_service     = BalanceService(engine, income_repo, charge_repo, tx_repo)
    except Exception:
        import traceback
        traceback.print_exc()
        return 1

    window = MainWindow()

    # Each controller gets its page's view (public attribute on MainWindow) and
    # the services it needs. Storing them as locals keeps them alive (no GC).
    # register_page_enter(index, fn) makes the MainWindow call that function
    # every time the user navigates to that page, so data refreshes on nav.
    # The initial .refresh() call populates data for first render.

    dashboard_ctrl = DashboardController(
        view=window,
        session_service=session_service,
        balance_service=balance_service,
        income_service=income_service,
        charge_service=charge_service,
        fuzzy_charge_service=fuzzy_charge_service,
        spend_service=spend_service,
        caution_threshold=_CAUTION_THRESHOLD,
    )
    window.register_page_enter(0, dashboard_ctrl.refresh)
    dashboard_ctrl.refresh()

    activity_ctrl = ActivityController(
        view=window.activity_page,
        session_service=session_service,
        income_service=income_service,
        spend_service=spend_service,
        charge_service=charge_service,
    )
    window.register_page_enter(1, activity_ctrl.refresh)
    activity_ctrl.refresh()

    insights_ctrl = InsightsController(
        view=window.insights_page,
        session_service=session_service,
        balance_service=balance_service,
        spend_service=spend_service,
        charge_service=charge_service,
        fuzzy_charge_service=fuzzy_charge_service,
    )
    window.register_page_enter(2, insights_ctrl.refresh)
    insights_ctrl.refresh()

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
