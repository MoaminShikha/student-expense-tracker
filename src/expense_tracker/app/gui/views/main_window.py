from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui.constants import PageIndex
from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.views.dashboard_page import DashboardPage
from expense_tracker.app.gui.views.activity_page import ActivityPage
from expense_tracker.app.gui.views.insights_page import InsightsPage
from expense_tracker.app.gui.views.settings_page import SettingsPage
from expense_tracker.app.gui.widgets.panels import ChargeRowVM, TxRowVM, CategoryRowVM
from expense_tracker.app.gui.widgets.sidebar import Sidebar
from expense_tracker.app.gui.widgets.topbar import Topbar

if TYPE_CHECKING:
    from expense_tracker.app.gui.view_models.balance_view_model import BalanceViewModel


class MainWindow(QMainWindow):
    """
    Main application window with QStackedWidget page management.

    Two-column layout: Sidebar (fixed) + Main area (topbar + stacked pages).
    Emits signals for user actions — no business logic.
    """

    # ── SIGNALS ───────────────────────────────────────────────────────────────
    refresh_requested    = pyqtSignal()
    add_income_requested = pyqtSignal()
    add_spend_requested  = pyqtSignal()
    add_charge_requested = pyqtSignal()

    _PAGE_NAMES: dict[str, str] = {
        "dashboard": "DASHBOARD / 01",
        "activity":  "ACTIVITY / 01",
        "insights":  "INSIGHTS / 01",
        "settings":  "SETTINGS / 01",
    }

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Mizān")
        self.setMinimumSize(1280, 720)

        self._sidebar = Sidebar()
        self._topbar  = Topbar()
        self._stack   = QStackedWidget()

        # Dict[page_index, callback] — callback fires when nav switches to that page.
        # Registered in main.py via register_page_enter() so each page's controller
        # can call .refresh() automatically on navigation.
        self._on_page_enter: dict[int, callable] = {}

        # Pages are public attributes so controllers (wired in main.py) can
        # call their set_* methods (e.g. activity_page.set_ledger(...)).
        # Signals from DashboardPage's "Add" buttons are forwarded up through
        # MainWindow signals, where controllers can connect to them.
        self.dashboard_page = DashboardPage(
            add_income_signal=self.add_income_requested,
            add_spend_signal=self.add_spend_requested,
            add_charge_signal=self.add_charge_requested,
        )
        self.activity_page  = ActivityPage(
            add_income_signal=self.add_income_requested,
            add_spend_signal=self.add_spend_requested,
            add_charge_signal=self.add_charge_requested,
        )
        self.insights_page  = InsightsPage()
        self.settings_page  = SettingsPage()

        # Add pages to stack in PageIndex order
        self._stack.addWidget(self.dashboard_page)
        self._stack.addWidget(self.activity_page)
        self._stack.addWidget(self.insights_page)
        self._stack.addWidget(self.settings_page)

        # Sidebar nav click → switch page in stack
        self._sidebar.nav_changed.connect(self._on_nav_changed)

        # Topbar sync button → re-fires as MainWindow-level signal
        self._topbar.refresh_requested.connect(self.refresh_requested.emit)

        # Set focus policy for keyboard navigation
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.setCentralWidget(self._build_root())

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        """Handle keyboard navigation between pages."""
        # Alt+1/2/3/4 for quick navigation
        if event.modifiers() == Qt.KeyboardModifier.AltModifier:
            key_map = {
                Qt.Key.Key_1: PageIndex.DASHBOARD,
                Qt.Key.Key_2: PageIndex.ACTIVITY,
                Qt.Key.Key_3: PageIndex.INSIGHTS,
                Qt.Key.Key_4: PageIndex.SETTINGS,
            }
            if event.key() in key_map:
                self._stack.setCurrentIndex(key_map[event.key()])
                event.accept()
                return

        # Ctrl+R for refresh
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_R:
            self.refresh_requested.emit()
            event.accept()
            return

        super().keyPressEvent(event)

    # ── PAGE SWITCHING ─────────────────────────────────────────────────────────

    def _on_nav_changed(self, key: str) -> None:
        # Map nav key → QStackedWidget index, switch page, update breadcrumb
        mapping = {
            "dashboard": PageIndex.DASHBOARD,
            "activity": PageIndex.ACTIVITY,
            "insights": PageIndex.INSIGHTS,
            "settings": PageIndex.SETTINGS,
        }
        idx = mapping.get(key, PageIndex.DASHBOARD)
        self._stack.setCurrentIndex(idx)
        self._topbar.set_breadcrumb(self._PAGE_NAMES.get(key, "DASHBOARD / 01"))
        # Fire the page-enter callback (registered by controllers in main.py) so
        # data refreshes every time the user navigates to that page.
        cb = self._on_page_enter.get(idx)
        if cb:
            cb()

    # ── PUBLIC SETTERS (delegate to DashboardPage) ────────────────────────────
    # DashboardController calls these on the MainWindow. Most proxy straight
    # through to dashboard_page.* so the controller doesn't need to know about
    # the QStackedWidget extraction. Topbar state (on_track, last_sync) is
    # updated here since it lives outside the stacked pages.

    def set_snapshot(
        self,
        snapshot: BalanceViewModel,
        last_sync: datetime | None = None,
        animate: bool = True,
    ) -> None:
        self.dashboard_page.set_snapshot(snapshot, last_sync, animate)
        self._topbar.set_on_track_state(snapshot.on_track_state_value)
        if last_sync:
            self._topbar.set_last_sync(last_sync.strftime("%d %b · %H:%M"))

    def set_upcoming(self, rows: Iterable[ChargeRowVM]) -> None:
        self.dashboard_page.set_upcoming(rows)

    def set_recent(self, rows: Iterable[TxRowVM]) -> None:
        self.dashboard_page.set_recent(rows)

    def set_categories(self, rows: Iterable[CategoryRowVM]) -> None:
        self.dashboard_page.set_categories(rows)

    def set_alert(self, body_html: str, amount_str: str, visible: bool) -> None:
        self.dashboard_page.set_alert(body_html, amount_str, visible)

    def set_last_sync(self, dt: datetime | None) -> None:
        if dt:
            self._topbar.set_last_sync(dt.strftime("%d %b · %H:%M"))

    def register_page_enter(self, index: int, callback: callable) -> None:
        """Register a callback (typically a controller's .refresh) to fire when
        the user navigates to the page at the given stack index."""
        self._on_page_enter[index] = callback

    def update_timeline(
        self,
        spent_pct: float,
        committed_pct: float,
        fuzzy_left_pct: float,
        fuzzy_width_pct: float,
        today_pct: float,
    ) -> None:
        self.dashboard_page._hero.timeline.set_percentages(
            spent_pct, committed_pct, fuzzy_left_pct, fuzzy_width_pct, today_pct
        )

    # ── ROOT LAYOUT ───────────────────────────────────────────────────────────

    def _build_root(self) -> QWidget:
        """Two-column root: Sidebar | Main area."""
        root = QWidget()
        root.setObjectName("appRoot")

        h = QHBoxLayout(root)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        h.addWidget(self._sidebar)
        sidebar_divider = QFrame()
        sidebar_divider.setObjectName("sidebarDivider")
        sidebar_divider.setFixedWidth(1)
        h.addWidget(sidebar_divider)
        h.addWidget(self._build_main_area(), stretch=1)

        root.setStyleSheet(f"""
            QWidget#appRoot {{
                background: {tokens.BG};
            }}
            QFrame#sidebarDivider {{
                background: {tokens.HAIRLINE_S};
                border: none;
            }}
        """)
        return root

    def _build_main_area(self) -> QWidget:
        """Topbar + stacked pages."""
        w = QWidget()
        w.setObjectName("mainArea")

        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        v.addWidget(self._topbar)

        divider = QFrame()
        divider.setObjectName("topbarDivider")
        divider.setFixedHeight(1)
        v.addWidget(divider)

        v.addWidget(self._stack, stretch=1)

        w.setStyleSheet(f"""
            QWidget#mainArea {{
                background: {tokens.BG};
            }}
            QFrame#topbarDivider {{
                background: {tokens.HAIRLINE};
            }}
        """)
        return w
