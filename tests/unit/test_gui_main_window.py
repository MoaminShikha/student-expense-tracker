from __future__ import annotations

import pytest

from expense_tracker.app.gui.views.main_window import MainWindow
from expense_tracker.app.gui.widgets.timeline_widget import TimelineWidget
from expense_tracker.app.gui.view_models.balance_view_model import BalanceViewModel


class TestMainWindowPublicAPI:
    """Smoke tests for MainWindow public API — no GUI rendering required."""

    def test_main_window_imports(self) -> None:
        """MainWindow class is importable."""
        assert MainWindow is not None

    def test_timeline_widget_imports(self) -> None:
        """TimelineWidget is importable."""
        assert TimelineWidget is not None

    def test_balance_view_model_imports(self) -> None:
        """BalanceViewModel is importable."""
        assert BalanceViewModel is not None

    def test_main_window_has_refresh_signal(self) -> None:
        """MainWindow exposes refresh_requested signal."""
        assert hasattr(MainWindow, "refresh_requested")

    def test_main_window_has_add_income_signal(self) -> None:
        """MainWindow exposes add_income_requested signal."""
        assert hasattr(MainWindow, "add_income_requested")

    def test_main_window_has_add_spend_signal(self) -> None:
        """MainWindow exposes add_spend_requested signal."""
        assert hasattr(MainWindow, "add_spend_requested")

    def test_main_window_has_add_charge_signal(self) -> None:
        """MainWindow exposes add_charge_requested signal."""
        assert hasattr(MainWindow, "add_charge_requested")

    def test_main_window_has_set_snapshot_method(self) -> None:
        """MainWindow has set_snapshot public method."""
        assert hasattr(MainWindow, "set_snapshot")
        assert callable(getattr(MainWindow, "set_snapshot"))

    def test_main_window_has_set_upcoming_method(self) -> None:
        """MainWindow has set_upcoming public method."""
        assert hasattr(MainWindow, "set_upcoming")
        assert callable(getattr(MainWindow, "set_upcoming"))

    def test_main_window_has_set_recent_method(self) -> None:
        """MainWindow has set_recent public method."""
        assert hasattr(MainWindow, "set_recent")
        assert callable(getattr(MainWindow, "set_recent"))

    def test_main_window_has_set_categories_method(self) -> None:
        """MainWindow has set_categories public method."""
        assert hasattr(MainWindow, "set_categories")
        assert callable(getattr(MainWindow, "set_categories"))

    def test_main_window_has_update_timeline_method(self) -> None:
        """MainWindow has update_timeline public method."""
        assert hasattr(MainWindow, "update_timeline")
        assert callable(getattr(MainWindow, "update_timeline"))

    def test_main_window_has_set_last_sync_method(self) -> None:
        """MainWindow has set_last_sync public method."""
        assert hasattr(MainWindow, "set_last_sync")
        assert callable(getattr(MainWindow, "set_last_sync"))

