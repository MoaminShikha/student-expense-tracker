from __future__ import annotations

from datetime import datetime
from typing import Iterable

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from expense_tracker.app.gui_v2 import tokens
from expense_tracker.app.gui_v2.constants import PAGE_NAMES, PageIndex
from expense_tracker.app.gui_v2.view_models.balance_view_model import BalanceViewModel
from expense_tracker.app.gui_v2.widgets.panels import CategoryRowVM, ChargeRowVM, TxRowVM
from expense_tracker.app.gui_v2.widgets.sidebar import Sidebar
from expense_tracker.app.gui_v2.widgets.topbar import Topbar
from expense_tracker.app.gui_v2.views.activity_page import ActivityPage
from expense_tracker.app.gui_v2.views.dashboard_page import DashboardPage
from expense_tracker.app.gui_v2.views.insights_page import InsightsPage
from expense_tracker.app.gui_v2.views.settings_page import SettingsPage


class MainWindow(QMainWindow):
    """
    Root application window for GUI v2.

    Keyboard shortcuts:
        Alt+1 → Dashboard
        Alt+2 → Activity
        Alt+3 → Insights
        Alt+4 → Settings
        Ctrl+R → Refresh (delegates to topbar refresh_requested)
    """

    add_income_requested  = pyqtSignal()
    add_spend_requested   = pyqtSignal()
    add_charge_requested  = pyqtSignal()
    refresh_requested     = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ميزان — Student Budget")
        self.setMinimumSize(1060, 680)

        # Widgets
        self._sidebar = Sidebar()
        self._topbar  = Topbar()
        self._stack   = QStackedWidget()
        self._dash    = DashboardPage()
        self._act     = ActivityPage()
        self._ins     = InsightsPage()
        self._sett    = SettingsPage()

        self._stack.addWidget(self._dash)   # index 0
        self._stack.addWidget(self._act)    # index 1
        self._stack.addWidget(self._ins)    # index 2
        self._stack.addWidget(self._sett)   # index 3

        self._opacity = QGraphicsOpacityEffect(self._stack)
        self._opacity.setOpacity(1.0)
        self._stack.setGraphicsEffect(self._opacity)
        self._fade_anim = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade_anim.setDuration(150)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Forward DashboardPage signals
        self._dash.add_income_requested.connect(self.add_income_requested)
        self._dash.add_spend_requested.connect(self.add_spend_requested)
        self._dash.add_charge_requested.connect(self.add_charge_requested)
        self._topbar.refresh_requested.connect(self.refresh_requested)

        # Sidebar / page switching
        self._sidebar.page_selected.connect(self._switch_page)

        # Keyboard shortcuts
        QShortcut(QKeySequence("Alt+1"), self).activated.connect(lambda: self._switch_page(0))
        QShortcut(QKeySequence("Alt+2"), self).activated.connect(lambda: self._switch_page(1))
        QShortcut(QKeySequence("Alt+3"), self).activated.connect(lambda: self._switch_page(2))
        QShortcut(QKeySequence("Alt+4"), self).activated.connect(lambda: self._switch_page(3))
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.refresh_requested)

        self._build_layout()

    # ── FACADE PUBLIC API ─────────────────────────────────────────────────────

    def set_snapshot(self, vm: BalanceViewModel) -> None:
        """Delegate snapshot to DashboardPage and update topbar on-track state."""
        self._dash.set_snapshot(vm)
        self._topbar.set_on_track_state(vm.on_track_state_value)

    def set_upcoming(self, rows: Iterable[ChargeRowVM]) -> None:
        """Delegate upcoming charge rows to DashboardPage."""
        self._dash.set_upcoming(rows)

    def set_recent(self, rows: Iterable[TxRowVM]) -> None:
        """Delegate recent transaction rows to DashboardPage."""
        self._dash.set_recent(rows)

    def set_categories(self, rows: Iterable[CategoryRowVM]) -> None:
        """Delegate category breakdown rows to DashboardPage."""
        self._dash.set_categories(rows)

    def set_timeline_percentages(
        self,
        spent_pct: float,
        committed_pct: float,
        fuzzy_left_pct: float,
        fuzzy_width_pct: float,
        today_pct: float,
    ) -> None:
        """Delegate timeline percentages to DashboardPage."""
        self._dash.set_timeline_percentages(
            spent_pct, committed_pct, fuzzy_left_pct, fuzzy_width_pct, today_pct
        )

    def set_alert(self, body_html: str, amount_str: str, visible: bool) -> None:
        """Delegate alert state to DashboardPage."""
        self._dash.set_alert(body_html, amount_str, visible)

    def set_last_sync(self, dt: datetime | None) -> None:
        """Update the topbar last-sync timestamp."""
        if dt is None:
            return
        self._topbar.set_last_sync(dt.strftime("%H:%M"))

    def update_timeline(
        self,
        spent_pct: float,
        committed_pct: float,
        fuzzy_left_pct: float,
        fuzzy_width_pct: float,
        today_pct: float,
    ) -> None:
        """Alias for set_timeline_percentages."""
        self.set_timeline_percentages(
            spent_pct, committed_pct, fuzzy_left_pct, fuzzy_width_pct, today_pct
        )

    # ── LAYOUT ────────────────────────────────────────────────────────────────

    def _build_layout(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        content_col = QWidget()
        content_layout = QHBoxLayout(content_col)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self._sidebar)
        content_layout.addWidget(self._stack, stretch=1)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self._build_right_col())

    def _build_right_col(self) -> QWidget:
        col = QWidget()
        layout = QHBoxLayout(col)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._sidebar)
        right = QWidget()
        right_layout = QHBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        from PyQt6.QtWidgets import QVBoxLayout
        right_col = QWidget()
        rc_layout = QVBoxLayout(right_col)
        rc_layout.setContentsMargins(0, 0, 0, 0)
        rc_layout.setSpacing(0)
        rc_layout.addWidget(self._topbar)
        rc_layout.addWidget(self._stack, stretch=1)
        layout.addWidget(right_col, stretch=1)
        return col

    def _switch_page(self, index: int) -> None:
        if self._stack.currentIndex() == index:
            return
        self._fade_anim.stop()
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._stack.setCurrentIndex(index)
        self._opacity.setOpacity(0.0)
        self._fade_anim.start()
        key = {0: "dashboard", 1: "activity", 2: "insights", 3: "settings"}.get(index, "dashboard")
        self._topbar.set_breadcrumb(PAGE_NAMES.get(key, ""))
