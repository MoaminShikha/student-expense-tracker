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
    from expense_tracker.app.gui.views.main_window import MainWindow

from expense_tracker.app.gui.view_models.balance_view_model import BalanceViewModel
from expense_tracker.shared.exceptions import ApplicationError, ValidationError


class DashboardController:
    """
    Thin orchestrator connecting MainWindow signals with application services.

    Owns no domain state. Receives signals from the view, calls services,
    converts results into view models, and calls the view's public setters.
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
            logger: logging.Logger | None = None, ) -> None:
        self._view = view
        self._session_service = session_service
        self._balance_service = balance_service
        self._income_service = income_service
        self._charge_service = charge_service
        self._fuzzy_charge_service = fuzzy_charge_service
        self._spend_service = spend_service
        self._caution_threshold = Decimal("100") if caution_threshold is None else caution_threshold
        self._logger = logger or logging.getLogger(__name__)

        # Wire MainWindow signals → controller action handlers.
        # DashboardPage's "Add" buttons emit these signals through the
        # MainWindow proxy (see main_window.py signal declarations).
        self._view.refresh_requested.connect(self._on_refresh_requested)
        self._view.add_income_requested.connect(self._on_add_income_requested)
        self._view.add_spend_requested.connect(self._on_add_spend_requested)
        self._view.add_charge_requested.connect(self._on_add_charge_requested)

    def refresh(self) -> None:
        """Fetch latest data from services and push it into the view."""
        if not self._balance_service or not self._session_service:
            self._logger.debug("Skipping refresh: missing services")
            return

        session = self._session_service.get_active()
        if session is None:
            self._logger.debug("No active session — dashboard refresh skipped")
            return

        try:
            snapshot = self._balance_service.aggregate_and_build_snapshot(session.session_id, self._caution_threshold,
                                                                          session.opening_balance, )
            view_model = self._build_view_model(snapshot, session_id=session.session_id)
            self._view.set_snapshot(view_model, last_sync=None)
            self._view.set_timeline_percentages(
                view_model.timeline_spent_pct,
                view_model.timeline_committed_pct,
                view_model.timeline_fuzzy_left_pct,
                view_model.timeline_fuzzy_width_pct,
                view_model.today_pct,
            )

            today = date.today()

            # Populate upcoming charges
            if self._charge_service:
                try:
                    upcoming = self._charge_service.get_charges_for_month(session.session_id, today.year, today.month)
                    upcoming_rows = [self._charge_to_row(c) for c in upcoming]
                    self._view.set_upcoming(upcoming_rows)
                except Exception:
                    self._logger.debug("Could not load upcoming charges", exc_info=True)

            # Populate recent transactions
            if self._spend_service:
                try:
                    recent = self._spend_service.list_for_month(session.session_id, today.year, today.month)
                    recent = sorted(recent, key=lambda t: t.date, reverse=True)[:5]
                    recent_rows = [self._tx_to_row(tx) for tx in recent]
                    self._view.set_recent(recent_rows)
                except Exception:
                    self._logger.debug("Could not load recent transactions", exc_info=True)

            # Populate category breakdown (calculate from all month transactions)
            if self._spend_service:
                try:
                    all_txs = self._spend_service.list_for_month(session.session_id, today.year, today.month)
                    cat_totals: dict = {}
                    total_spent = Decimal("0")
                    for tx in all_txs:
                        cat_key = tx.category.value if tx.category else "other"
                        cat_name = tx.category.value.capitalize() if tx.category else "Other"
                        if cat_name not in cat_totals:
                            cat_totals[cat_name] = Decimal("0")
                        cat_totals[cat_name] += tx.amount
                        total_spent += tx.amount

                    cat_rows = []
                    for cat_name, amount in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True):
                        pct = float((amount / total_spent * 100)) if total_spent > 0 else 0.0
                        cat_rows.append(self._cat_to_row((cat_name, amount, pct)))
                    self._view.set_categories(cat_rows)
                except Exception:
                    self._logger.debug("Could not load category breakdown", exc_info=True)

            self._logger.debug("Dashboard refreshed")
        except (ValidationError, ApplicationError) as e:
            self._logger.warning("Failed to refresh dashboard: %s", e)
        except Exception:
            self._logger.exception("Unexpected error refreshing dashboard")

    # ── Signal handlers ───────────────────────────────────────────────────────

    def _on_refresh_requested(self) -> None:
        self.refresh()

    def _on_add_income_requested(self) -> None:
        if self._income_service is None:
            return
        from expense_tracker.app.gui.dialogs.add_income_dialog import AddIncomeDialog
        from PyQt6.QtWidgets import QMessageBox
        dlg = AddIncomeDialog()
        if dlg.exec():
            try:
                self._income_service.add_income(dlg.amount, dlg.source_tag, dlg.entry_date)
                self.refresh()
            except ValidationError as e:
                self._logger.warning("Invalid income entry: %s", e)
            except ApplicationError as e:
                self._logger.warning("Could not add income: %s", e)
            except Exception:
                self._logger.exception("Unexpected error adding income")

    def _on_add_spend_requested(self) -> None:
        if self._spend_service is None:
            return
        from expense_tracker.app.gui.dialogs.add_spend_dialog import AddSpendDialog
        from PyQt6.QtWidgets import QMessageBox
        dlg = AddSpendDialog()
        if dlg.exec():
            try:
                self._spend_service.add_transaction(dlg.amount, dlg.description, dlg.category, dlg.spent_on)
                self.refresh()
            except ValidationError as e:
                self._logger.warning("Invalid spend entry: %s", e)
            except ApplicationError as e:
                self._logger.warning("Could not add spend: %s", e)
            except Exception:
                self._logger.exception("Unexpected error adding spend")

    def _on_add_charge_requested(self) -> None:
        if self._charge_service is None:
            return
        from expense_tracker.app.gui.dialogs.add_charge_dialog import AddChargeDialog
        from PyQt6.QtWidgets import QMessageBox
        dlg = AddChargeDialog()
        if dlg.exec():
            try:
                if dlg.is_recurring:
                    self._charge_service.add_recurring_charge(dlg.name, dlg.amount, dlg.day_of_month, dlg.reminder_days)
                else:
                    self._charge_service.add_charge(dlg.name, dlg.amount, dlg.due_date)
                self.refresh()
            except ValidationError as e:
                self._logger.warning("Invalid charge entry: %s", e)
            except ApplicationError as e:
                self._logger.warning("Could not add charge: %s", e)
            except Exception:
                self._logger.exception("Unexpected error adding charge")

    # ── Presentation mapping ──────────────────────────────────────────────────

    def _build_view_model(self, snapshot: BalanceSnapshot, session_id=None) -> BalanceViewModel:
        """Convert a domain BalanceSnapshot into a UI-shaped BalanceViewModel.
        
        Adds extra computations that don't live in the domain layer:
        timeline percentages, committed/fuzzy charges breakdown for the
        month, and committed/fuzzy timeline widths for the dual-track widget.
        """

        def fmt(amount: Decimal) -> str:
            return f"₪{amount:,.0f}"

        today = date.today()
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        today_pct = float(today.day / days_in_month * 100)

        budget = snapshot.monthly_budget
        if budget > Decimal("0"):
            spent_pct = float(min(Decimal("100"), snapshot.monthly_spent / budget * Decimal("100")))
        else:
            spent_pct = 0.0

        monthly_committed = Decimal("0")
        committed_pct = 0.0
        committed_due_pcts: list[float] = []
        fuzzy_total = Decimal("0")
        fuzzy_left_pct = 0.0
        fuzzy_width_pct = 0.0

        # ── Committed charges for timeline ─────────────────────────────────
        # Sum all upcoming charges due this month. committed_pct is the
        # width of the RED segment on the budget bar — it starts at the
        # right edge of the spent (gold) segment.
        if session_id is not None and self._charge_service is not None and budget > Decimal("0"):
            try:
                charges = self._charge_service.get_charges_for_month(
                    session_id, today.year, today.month
                )
                monthly_committed = sum((c.amount for c in charges), Decimal("0"))
                committed_pct = float(min(
                    Decimal("100") - Decimal(str(spent_pct)),
                    monthly_committed / budget * Decimal("100"),
                ))
                committed_due_pcts = [
                    float(c.due_date.day / days_in_month * 100)
                    for c in charges
                ]
            except Exception:
                self._logger.debug("Could not compute committed data", exc_info=True)

        # ── Fuzzy charges for timeline ────────────────────────────────────
        # Fuzzy charges (known date, unknown amount) appear as a hatched
        # segment on the budget bar, placed right after committed.
        if session_id is not None and self._fuzzy_charge_service is not None and budget > Decimal("0"):
            try:
                fuzzy_list = self._fuzzy_charge_service.list_pending_for_month(
                    session_id, today.year, today.month
                )
                # Sum of estimated amounts; default to 0 if no estimate
                fuzzy_estimates = [
                    f.estimated_amount for f in fuzzy_list
                    if f.estimated_amount is not None
                ]
                fuzzy_total = sum(fuzzy_estimates, Decimal("0"))
                fuzzy_left_pct = spent_pct + committed_pct
                fuzzy_width_pct = float(min(
                    Decimal("100") - Decimal(str(spent_pct)) - Decimal(str(committed_pct)),
                    fuzzy_total / budget * Decimal("100"),
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

    def _charge_to_row(self, charge) -> 'ChargeRowVM':
        """Convert CommittedCharge domain object to ChargeRowVM for UI."""
        from datetime import datetime
        from expense_tracker.app.gui.widgets.panels import ChargeRowVM

        days_until = (charge.due_date - date.today()).days
        if days_until < 0:
            relative = "Overdue"
        elif days_until == 0:
            relative = "Today"
        elif days_until == 1:
            relative = "Tomorrow"
        else:
            relative = f"in {days_until} days"

        return ChargeRowVM(
            name=charge.name,
            amount_str=f"₪{charge.amount:,.0f}",
            due_str=charge.due_date.strftime("%d %b"),
            relative_str=relative,
            recurring=charge.recurring_rule_id is not None,
        )

    def _tx_to_row(self, tx) -> 'TxRowVM':
        """Convert Transaction domain object to TxRowVM for UI."""
        from expense_tracker.app.gui.widgets.panels import TxRowVM

        return TxRowVM(
            name=tx.description,
            category_key=tx.category.value,
            place="",
            amount_str=f"₪{tx.amount:,.0f}",
            timestamp_str=tx.date.strftime("%d %b"),
        )

    def _cat_to_row(self, cat_tuple) -> 'CategoryRowVM':
        """Convert category breakdown tuple to CategoryRowVM for UI."""
        from expense_tracker.app.gui.widgets.panels import CategoryRowVM

        category_name, amount, pct = cat_tuple
        return CategoryRowVM(
            name=category_name,
            key=category_name.lower(),
            amount_str=f"₪{amount:,.0f}",
            pct=pct,
        )
