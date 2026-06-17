from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from expense_tracker.application.services import BalanceService, ChargeService, FuzzyChargeService, SessionService, SpendService
    from expense_tracker.app.gui_v2.views.insights_page import InsightsPage


class InsightsController:
    """Orchestrates the insights page for GUI v2.

    Currently a stub — the InsightsPage view is minimal and will be expanded
    in a future iteration when charts are wired in.
    """

    def __init__(
        self,
        view: InsightsPage,
        session_service: SessionService | None = None,
        balance_service: BalanceService | None = None,
        spend_service: SpendService | None = None,
        charge_service: ChargeService | None = None,
        fuzzy_charge_service: FuzzyChargeService | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._view                = view
        self._session_service     = session_service
        self._balance_service     = balance_service
        self._spend_service       = spend_service
        self._charge_service      = charge_service
        self._fuzzy_charge_service = fuzzy_charge_service
        self._logger              = logger or logging.getLogger(__name__)

    def refresh(self) -> None:
        if not self._session_service:
            return
        session = self._session_service.get_active()
        if session is None:
            return
        # Chart population will go here once InsightsPage gains proper widgets.
        self._logger.debug("InsightsController (v2) refresh called — stub")
