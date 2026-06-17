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
from expense_tracker.app.gui_v2.fonts import load_fonts
from expense_tracker.app.gui_v2.stylesheet import build_stylesheet
# Force light mode on the gui/ theme manager singleton so it can't
# override the v2 stylesheet if any gui/ widget imports it.
from expense_tracker.app.gui.styles.theme_manager import get_theme_manager as _get_tm
from expense_tracker.app.gui_v2.controllers.activity_controller import ActivityController
from expense_tracker.app.gui_v2.controllers.dashboard_controller import DashboardController
from expense_tracker.app.gui_v2.controllers.insights_controller import InsightsController
from expense_tracker.app.gui_v2.views.main_window import MainWindow

_CAUTION_THRESHOLD = Decimal("100")


def main() -> int:
    import logging
    logger = logging.getLogger(__name__)
    app = QApplication(sys.argv)
    load_fonts()
    # Lock the gui/ theme manager to light so it can't push dark QSS over us.
    _tm = _get_tm()
    _tm._theme = "light"
    app.setStyleSheet(build_stylesheet("light"))

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
        logger.exception("Failed to initialize application")
        return 1

    # Show onboarding if no active session exists
    session = session_service.get_active()
    if session is None:
        from expense_tracker.app.gui_v2.dialogs.onboarding_dialog import OnboardingDialog
        dlg = OnboardingDialog()
        if dlg.exec():
            session_service.create_session(dlg.opening_balance)
        else:
            return 0  # user cancelled first-run setup

    window = MainWindow()

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
    dashboard_ctrl.refresh()

    activity_ctrl = ActivityController(
        view=window._act,
        session_service=session_service,
        income_service=income_service,
        spend_service=spend_service,
        charge_service=charge_service,
    )
    activity_ctrl.refresh()

    insights_ctrl = InsightsController(
        view=window._ins,
        session_service=session_service,
        balance_service=balance_service,
        spend_service=spend_service,
        charge_service=charge_service,
        fuzzy_charge_service=fuzzy_charge_service,
    )
    insights_ctrl.refresh()

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
