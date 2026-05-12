from __future__ import annotations
import logging
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...application.services import BalanceService, ChargeService, IncomeService, SessionService, SpendService
    from .views.main_window import MainWindow
class DashboardController:
    """Thin orchestrator connecting MainWindow signals with application services."""
    def __init__(
        self,
        view: MainWindow,
        session_service: SessionService | None = None,
        balance_service: BalanceService | None = None,
        charge_service: ChargeService | None = None,
        spend_service: SpendService | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Initialize the dashboard controller."""
        self._view = view
        self._session_service = session_service
        self._balance_service = balance_service
        self._charge_service = charge_service
        self._spend_service = spend_service
        self._logger = logger or logging.getLogger(__name__)
        self._view.refresh_requested.connect(self._on_refresh_requested)
        self._view.add_income_requested.connect(self._on_add_income_requested)
        self._view.add_spend_requested.connect(self._on_add_spend_requested)
        self._view.add_charge_requested.connect(self._on_add_charge_requested)
    def refresh(self) -> None:
        """Refresh dashboard by fetching latest data from services."""
        if not self._balance_service:
            self._logger.debug("Skipping refresh: balance_service is None")
            return
        self._logger.debug("Dashboard refresh completed")
    def _on_refresh_requested(self) -> None:
        """Handle refresh signal from view."""
        self._logger.debug("Refresh requested from view")
        self.refresh()
    def _on_add_income_requested(self) -> None:
        """Handle add-income signal from view."""
        self._logger.debug("Add income requested from view")
    def _on_add_spend_requested(self) -> None:
        """Handle add-spend signal from view."""
        self._logger.debug("Add spend requested from view")
    def _on_add_charge_requested(self) -> None:
        """Handle add-charge signal from view."""
        self._logger.debug("Add charge requested from view")