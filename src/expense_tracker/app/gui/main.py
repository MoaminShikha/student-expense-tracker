from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

# Set to True to launch the new GUI v2 instead of the current GUI.
USE_GUI_V2 = True

from PyQt6.QtWidgets import QApplication

_HERE         = Path(__file__).resolve()
_SRC_DIR      = _HERE.parents[3]
_PROJECT_ROOT = _SRC_DIR.parent
_DATA_DIR     = _PROJECT_ROOT / "data"

if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from expense_tracker.app.composition import build_services
from expense_tracker.app.gui.constants import PageIndex
from expense_tracker.app.gui.styles.fonts import load_fonts
from expense_tracker.app.gui.styles.stylesheet_manager import apply_stylesheet
from expense_tracker.app.gui.styles.theme_manager import get_theme_manager
from expense_tracker.app.gui.controllers.activity_controller import ActivityController
from expense_tracker.app.gui.controllers.dashboard_controller import DashboardController
from expense_tracker.app.gui.controllers.insights_controller import InsightsController
from expense_tracker.app.gui.views.main_window import MainWindow

_CAUTION_THRESHOLD = Decimal("100")


def main() -> int:
    if USE_GUI_V2:
        from expense_tracker.app.gui_v2.main import main as main_v2
        return main_v2()

    import logging
    logger = logging.getLogger(__name__)
    app = QApplication([])
    load_fonts()
    theme_mgr = get_theme_manager()
    apply_stylesheet(app, theme_mgr.current_theme)

    try:
        services = build_services(_DATA_DIR, logger=logger)
    except Exception:
        logger.exception("Failed to initialize application")
        return 1

    session_service      = services.session_service
    income_service       = services.income_service
    charge_service       = services.charge_service
    fuzzy_charge_service = services.fuzzy_charge_service
    spend_service        = services.spend_service
    balance_service      = services.balance_service

    # First-run onboarding: without an active session every add silently no-ops
    # (services raise "No active session"), so collect an opening balance and
    # create the session before the main window loads.
    if session_service.get_active() is None:
        from expense_tracker.app.gui.dialogs.onboarding_dialog import OnboardingDialog

        onboarding = OnboardingDialog()
        if not onboarding.exec():
            logger.info("Onboarding cancelled before a session was created; exiting.")
            return 0
        try:
            session_service.init_session(onboarding.opening_balance)
        except Exception:
            logger.exception("Failed to create the initial session")
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
    window.register_page_enter(PageIndex.DASHBOARD, dashboard_ctrl.refresh)
    dashboard_ctrl.refresh()

    activity_ctrl = ActivityController(
        view=window.activity_page,
        session_service=session_service,
        income_service=income_service,
        spend_service=spend_service,
        charge_service=charge_service,
    )
    window.register_page_enter(PageIndex.ACTIVITY, activity_ctrl.refresh)
    activity_ctrl.refresh()

    insights_ctrl = InsightsController(
        view=window.insights_page,
        session_service=session_service,
        balance_service=balance_service,
        spend_service=spend_service,
        charge_service=charge_service,
        fuzzy_charge_service=fuzzy_charge_service,
    )
    window.register_page_enter(PageIndex.INSIGHTS, insights_ctrl.refresh)
    insights_ctrl.refresh()

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
