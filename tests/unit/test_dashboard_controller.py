from __future__ import annotations

from decimal import Decimal
from uuid import uuid4
from datetime import date

from expense_tracker.app.gui.controllers.dashboard_controller import DashboardController
from expense_tracker.app.gui.view_models.balance_view_model import BalanceViewModel
from expense_tracker.domain.models.balance import BalanceSnapshot, OnTrackState, BalanceState


class SignalStub:
    def __init__(self) -> None:
        self._connected = []

    def connect(self, cb):
        self._connected.append(cb)


class DummyView:
    def __init__(self) -> None:
        # emulate PyQt signal attributes used by the controller
        self.refresh_requested = SignalStub()
        self.add_income_requested = SignalStub()
        self.add_spend_requested = SignalStub()
        self.add_charge_requested = SignalStub()

        self.set_snapshot_called = False
        self.last_snapshot = None

    def set_snapshot(self, snapshot: BalanceViewModel, last_sync=None, animate: bool = True) -> None:
        self.set_snapshot_called = True
        self.last_snapshot = snapshot


class DummySessionService:
    def __init__(self, session):
        self._session = session

    def get_active(self):
        return self._session


class DummyBalanceService:
    def __init__(self, snapshot: BalanceSnapshot):
        self.snapshot = snapshot
        self.called = False

    def aggregate_and_build_snapshot(self, session_id, caution_threshold, opening_balance, red_threshold=None):
        self.called = True
        return self.snapshot


class SimpleSession:
    def __init__(self, session_id, opening_balance: Decimal):
        self.session_id = session_id
        self.opening_balance = opening_balance


def test_refresh_no_active_session():
    view = DummyView()
    session_service = DummySessionService(None)
    balance_service = DummyBalanceService(None)  # should not be called

    controller = DashboardController(view=view, session_service=session_service, balance_service=balance_service)

    # should not raise and should not call view.set_snapshot
    controller.refresh()
    assert view.set_snapshot_called is False
    assert balance_service.called is False


def test_refresh_with_active_session_and_snapshot():
    # Prepare a domain snapshot
    snapshot = BalanceSnapshot(
        free_money=Decimal("500"),
        monthly_budget=Decimal("1000"),
        monthly_spent=Decimal("200"),
        monthly_left=Decimal("800"),
        on_track_state=OnTrackState.GREEN,
        balance_state=BalanceState.NORMAL,
    )

    view = DummyView()
    session_id = uuid4()
    session = SimpleSession(session_id, opening_balance=Decimal("0"))
    session_service = DummySessionService(session)
    balance_service = DummyBalanceService(snapshot)

    controller = DashboardController(view=view, session_service=session_service, balance_service=balance_service)

    controller.refresh()

    assert balance_service.called is True
    assert view.set_snapshot_called is True
    vm = view.last_snapshot
    assert vm.free_money == Decimal("500")
    assert vm.free_money_str == "₪500"
    assert vm.monthly_budget == Decimal("1000")
    assert vm.monthly_spent == Decimal("200")
    # timeline spent percent = 200/1000*100 == 20.0
    assert abs(vm.timeline_spent_pct - 20.0) < 1e-6
    assert vm.balance_state_value == "normal"
    assert vm.on_track_state_value == "green"


