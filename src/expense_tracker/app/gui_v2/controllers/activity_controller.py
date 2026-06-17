from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from expense_tracker.application.services import ChargeService, IncomeService, SessionService, SpendService
    from expense_tracker.app.gui_v2.views.activity_page import ActivityPage

from expense_tracker.app.gui_v2.view_models.ledger_view_model import LedgerEntryVM


class ActivityController:
    """Orchestrates the activity/ledger page for GUI v2."""

    def __init__(
        self,
        view: ActivityPage,
        session_service: SessionService | None = None,
        income_service: IncomeService | None = None,
        spend_service: SpendService | None = None,
        charge_service: ChargeService | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._view            = view
        self._session_service = session_service
        self._income_service  = income_service
        self._spend_service   = spend_service
        self._charge_service  = charge_service
        self._logger          = logger or logging.getLogger(__name__)

    def refresh(self) -> None:
        if not self._session_service:
            return
        session = self._session_service.get_active()
        if session is None:
            return
        today = date.today()
        year, month = today.year, today.month
        try:
            raw: list[tuple[date, str, str, Decimal, str]] = []
            if self._income_service:
                for inc in self._income_service.list_for_month(session.session_id, year, month):
                    raw.append((inc.date, inc.source_tag.value.capitalize(), "income", inc.amount, inc.source_tag.value))
            if self._spend_service:
                for tx in self._spend_service.list_for_month(session.session_id, year, month):
                    raw.append((tx.date, tx.description, "spend", -tx.amount,
                                tx.category.value if tx.category else "other"))
            if self._charge_service:
                for ch in self._charge_service.list_all_for_month(session.session_id, year, month):
                    raw.append((ch.due_date, ch.name, "charge", -ch.amount, "Encumbrance"))

            raw.sort(key=lambda r: r[0])
            running = session.opening_balance
            entries: list[LedgerEntryVM] = []
            for dt, desc, etype, amt, cat in raw:
                running += amt
                prefix = "+" if amt > 0 else "−"
                entries.append(LedgerEntryVM(
                    date=dt, description=desc, entry_type=etype, amount=abs(amt),
                    amount_str=f"{prefix}₪{abs(amt):,.0f}",
                    running_balance=running, running_balance_str=f"₪{running:,.0f}",
                    category_str=cat,
                ))
            self._view.set_ledger(entries, session.opening_balance)
        except Exception:
            self._logger.exception("Failed to refresh activity ledger (v2)")
