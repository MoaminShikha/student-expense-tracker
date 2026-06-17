from __future__ import annotations

import calendar
import logging
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from expense_tracker.application.services import (
        BalanceService,
        ChargeService,
        FuzzyChargeService,
        IncomeService,
        SessionService,
        SpendService,
    )
    from expense_tracker.domain.models.balance import BalanceSnapshot
    from expense_tracker.app.gui_v2.views.main_window import MainWindow

from expense_tracker.app.gui_v2.view_models.balance_view_model import BalanceViewModel
from expense_tracker.app.gui_v2.widgets.panels import CategoryRowVM, ChargeRowVM, TxRowVM


class DashboardController:
    """
    Thin orchestrator connecting MainWindow (v2) signals with application services.

    Identical logic to gui/controllers/dashboard_controller.py but wired to
    gui_v2 view models and dialog imports.
    """

    def __init__(
        self,
        view: MainWindow,
        session_service: SessionService | None = None,
        balance_service: BalanceService | None = None,
        income_service: IncomeService | None = None,
        charge_service: ChargeService | None = None,
        fuzzy_charge_service: FuzzyChargeService | None = None,
        spend_service: SpendService | None = None,
        caution_threshold: Decimal | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._view                = view
        self._session_service     = session_service
        self._balance_service     = balance_service
        self._income_service      = income_service
        self._charge_service      = charge_service
        self._fuzzy_charge_service = fuzzy_charge_service
        self._spend_service       = spend_service
        self._caution_threshold   = Decimal("100") if caution_threshold is None else caution_threshold
        self._logger              = logger or logging.getLogger(__name__)

        view.refresh_requested.connect(self._on_refresh_requested)
        view.add_income_requested.connect(self._on_add_income_requested)
        view.add_spend_requested.connect(self._on_add_spend_requested)
        view.add_charge_requested.connect(self._on_add_charge_requested)

    def refresh(self) -> None:
        """Fetch latest data from services and push it into the view."""
        if not self._balance_service or not self._session_service:
            return
        session = self._session_service.get_active()
        if session is None:
            return
        try:
            snapshot = self._balance_service.aggregate_and_build_snapshot(
                session.session_id, self._caution_threshold, session.opening_balance,
            )
            vm = self._build_view_model(snapshot, session_id=session.session_id)
            self._view.set_snapshot(vm)
            self._view.set_timeline_percentages(
                vm.timeline_spent_pct,
                vm.timeline_committed_pct,
                vm.timeline_fuzzy_left_pct,
                vm.timeline_fuzzy_width_pct,
                vm.today_pct,
            )

            today = date.today()

            if self._charge_service:
                try:
                    charges = self._charge_service.get_charges_for_month(
                        session.session_id, today.year, today.month
                    )
                    self._view.set_upcoming([self._charge_to_row(c) for c in charges])
                except Exception:
                    self._logger.debug("Could not load upcoming charges", exc_info=True)

            if self._spend_service:
                try:
                    recent = self._spend_service.list_for_month(
                        session.session_id, today.year, today.month
                    )
                    recent = sorted(recent, key=lambda t: t.date, reverse=True)[:5]
                    self._view.set_recent([self._tx_to_row(tx) for tx in recent])
                except Exception:
                    self._logger.debug("Could not load recent transactions", exc_info=True)

            if self._spend_service:
                try:
                    all_txs = self._spend_service.list_for_month(
                        session.session_id, today.year, today.month
                    )
                    cat_totals: dict[str, Decimal] = {}
                    total_spent = Decimal("0")
                    for tx in all_txs:
                        name = (tx.category.value.capitalize() if tx.category else "Other")
                        cat_totals[name] = cat_totals.get(name, Decimal("0")) + tx.amount
                        total_spent += tx.amount
                    rows = []
                    for name, amt in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True):
                        pct = float(amt / total_spent * 100) if total_spent > 0 else 0.0
                        rows.append(CategoryRowVM(
                            name=name, key=name.lower(),
                            amount_str=f"₪{amt:,.0f}", pct=pct,
                        ))
                    self._view.set_categories(rows)
                except Exception:
                    self._logger.debug("Could not load categories", exc_info=True)

            self._logger.debug("Dashboard (v2) refreshed")
        except Exception:
            self._logger.exception("Failed to refresh dashboard (v2)")

    def _on_refresh_requested(self) -> None:
        self.refresh()

    def _on_add_income_requested(self) -> None:
        if self._income_service is None:
            return
        from expense_tracker.app.gui_v2.dialogs.add_income_dialog import AddIncomeDialog
        from PyQt6.QtWidgets import QMessageBox
        dlg = AddIncomeDialog(self._view)
        if dlg.exec():
            try:
                self._income_service.add_income(dlg.amount, dlg.source_tag, dlg.entry_date)
                self.refresh()
            except Exception as e:
                self._logger.exception("Failed to add income")
                QMessageBox.critical(self._view, "Error", str(e))

    def _on_add_spend_requested(self) -> None:
        if self._spend_service is None:
            return
        from expense_tracker.app.gui_v2.dialogs.add_spend_dialog import AddSpendDialog
        from PyQt6.QtWidgets import QMessageBox
        dlg = AddSpendDialog(self._view)
        if dlg.exec():
            try:
                self._spend_service.add_transaction(dlg.amount, dlg.description, dlg.category, dlg.spent_on)
                self.refresh()
            except Exception as e:
                self._logger.exception("Failed to add spend")
                QMessageBox.critical(self._view, "Error", str(e))

    def _on_add_charge_requested(self) -> None:
        if self._charge_service is None:
            return
        from expense_tracker.app.gui_v2.dialogs.add_charge_dialog import AddChargeDialog
        from PyQt6.QtWidgets import QMessageBox
        dlg = AddChargeDialog(self._view)
        if dlg.exec():
            try:
                if dlg.is_recurring:
                    self._charge_service.add_recurring_charge(dlg.name, dlg.amount, dlg.day_of_month, dlg.reminder_days)
                else:
                    self._charge_service.add_charge(dlg.name, dlg.amount, dlg.due_date)
                self.refresh()
            except Exception as e:
                self._logger.exception("Failed to add charge")
                QMessageBox.critical(self._view, "Error", str(e))

    # ── view-model building ───────────────────────────────────────────────────

    def _build_view_model(self, snapshot: BalanceSnapshot, session_id=None) -> BalanceViewModel:
        def fmt(a: Decimal) -> str:
            return f"₪{a:,.0f}"

        today = date.today()
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        today_pct = float(today.day / days_in_month * 100)
        budget = snapshot.monthly_budget

        spent_pct = (
            float(min(Decimal("100"), snapshot.monthly_spent / budget * 100))
            if budget > 0 else 0.0
        )

        monthly_committed = Decimal("0")
        committed_pct = 0.0
        committed_due_pcts: list[float] = []
        fuzzy_total = Decimal("0")
        fuzzy_left_pct = 0.0
        fuzzy_width_pct = 0.0

        if session_id is not None and self._charge_service and budget > 0:
            try:
                charges = self._charge_service.get_charges_for_month(
                    session_id, today.year, today.month
                )
                monthly_committed = sum((c.amount for c in charges), Decimal("0"))
                committed_pct = float(min(
                    Decimal("100") - Decimal(str(spent_pct)),
                    monthly_committed / budget * 100,
                ))
                committed_due_pcts = [
                    float(c.due_date.day / days_in_month * 100) for c in charges
                ]
            except Exception:
                self._logger.debug("Could not compute committed data", exc_info=True)

        if session_id is not None and self._fuzzy_charge_service and budget > 0:
            try:
                fuzzy_list = self._fuzzy_charge_service.list_pending_for_month(
                    session_id, today.year, today.month
                )
                estimates = [
                    f.estimated_amount for f in fuzzy_list if f.estimated_amount is not None
                ]
                fuzzy_total = sum(estimates, Decimal("0"))
                fuzzy_left_pct = spent_pct + committed_pct
                fuzzy_width_pct = float(min(
                    Decimal("100") - Decimal(str(spent_pct)) - Decimal(str(committed_pct)),
                    fuzzy_total / budget * 100,
                ))
            except Exception:
                self._logger.debug("Could not compute fuzzy data", exc_info=True)

        return BalanceViewModel(
            free_money=snapshot.free_money,
            free_money_str=fmt(snapshot.free_money),
            balance_state_value=snapshot.balance_state.value,
            monthly_budget=snapshot.monthly_budget,
            monthly_budget_str=fmt(snapshot.monthly_budget),
            monthly_spent=snapshot.monthly_spent,
            monthly_spent_str=fmt(snapshot.monthly_spent),
            monthly_committed=monthly_committed,
            monthly_committed_str=fmt(monthly_committed),
            monthly_fuzzy_estimated=fuzzy_total,
            monthly_fuzzy_estimated_str=fmt(fuzzy_total),
            monthly_left=snapshot.monthly_left,
            monthly_left_str=fmt(snapshot.monthly_left),
            on_track_state_value=snapshot.on_track_state.value,
            timeline_spent_pct=spent_pct,
            timeline_committed_pct=committed_pct,
            timeline_fuzzy_left_pct=fuzzy_left_pct,
            timeline_fuzzy_width_pct=fuzzy_width_pct,
            today_pct=today_pct,
            committed_due_pcts=committed_due_pcts,
        )

    def _charge_to_row(self, charge) -> ChargeRowVM:
        days_until = (charge.due_date - date.today()).days
        if days_until < 0:
            rel = "Overdue"
        elif days_until == 0:
            rel = "Today"
        elif days_until == 1:
            rel = "Tomorrow"
        else:
            rel = f"in {days_until} days"
        return ChargeRowVM(
            name=charge.name,
            amount_str=f"₪{charge.amount:,.0f}",
            due_str=charge.due_date.strftime("%d %b"),
            relative_str=rel,
            recurring=charge.recurring_rule_id is not None,
        )

    def _tx_to_row(self, tx) -> TxRowVM:
        return TxRowVM(
            name=tx.description,
            category_key=tx.category.value if tx.category else "other",
            place="",
            amount_str=f"₪{tx.amount:,.0f}",
            timestamp_str=tx.date.strftime("%d %b"),
        )
