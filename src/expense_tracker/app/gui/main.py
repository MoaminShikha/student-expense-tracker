from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

from PyQt6.QtWidgets import QApplication

_src_path = Path(__file__).resolve().parents[3]
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

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
from expense_tracker.app.gui.controllers.dashboard_controller import DashboardController
from expense_tracker.app.gui.views.main_window import MainWindow

_DATA_DIR = Path(__file__).resolve().parents[4] / "data"
_CAUTION_THRESHOLD = Decimal("100")


def main() -> int:
    """Start the PyQt6 desktop application with real services wired."""
    try:
        app = QApplication(sys.argv)
        load_fonts()

        session_repo      = JsonSessionRepository(_DATA_DIR / "session.json")
        income_repo       = JsonIncomeRepository(_DATA_DIR / "income.json")
        charge_repo       = JsonChargeRepository(_DATA_DIR / "charges.json")
        rule_repo         = JsonRecurringRuleRepository(_DATA_DIR / "recurring_rules.json")
        fuzzy_repo        = JsonFuzzyChargeRepository(_DATA_DIR / "fuzzy_charges.json")
        tx_repo           = JsonTransactionRepository(_DATA_DIR / "transactions.json")

        engine            = BalanceEngine()
        session_service   = SessionService(session_repo)
        income_service    = IncomeService(session_repo, income_repo)
        charge_service    = ChargeService(session_repo, charge_repo, rule_repo)
        fuzzy_service     = FuzzyChargeService(session_repo, fuzzy_repo, charge_repo, income_repo)
        spend_service     = SpendService(session_repo, tx_repo)
        balance_service   = BalanceService(engine, income_repo, charge_repo, tx_repo)

        window = MainWindow()
        controller = DashboardController(
            view=window,
            session_service=session_service,
            balance_service=balance_service,
            charge_service=charge_service,
            spend_service=spend_service,
            caution_threshold=_CAUTION_THRESHOLD,
        )
        controller.refresh()

        window.show()
        return app.exec()
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
