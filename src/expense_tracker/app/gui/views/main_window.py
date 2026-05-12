from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

if TYPE_CHECKING:
    from ..view_models.balance_view_model import BalanceViewModel


class TimelineWidget(QWidget):
    """
    Custom timeline visualization widget — presentation only.

    Renders a horizontal track showing monthly budget allocation:
    spent (red), committed (amber), fuzzy (light), and today marker.
    """

    def __init__(self) -> None:
        """Initialize timeline widget."""
        super().__init__()
        self.setMinimumHeight(40)
        self._spent_pct = 0.0
        self._committed_pct = 0.0
        self._fuzzy_left_pct = 0.0
        self._fuzzy_width_pct = 0.0
        self._today_pct = 0.0

    def set_percentages(
        self,
        spent_pct: float,
        committed_pct: float,
        fuzzy_left_pct: float,
        fuzzy_width_pct: float,
        today_pct: float,
    ) -> None:
        """
        Set timeline percentages for rendering.

        :param spent_pct: Percent of budget spent (0–100).
        :param committed_pct: Percent of budget committed (0–100).
        :param fuzzy_left_pct: Percent left in fuzzy range (0–100).
        :param fuzzy_width_pct: Width of fuzzy range (0–100).
        :param today_pct: Position of today marker (0–100).
        :return: None.
        """
        self._spent_pct = spent_pct
        self._committed_pct = committed_pct
        self._fuzzy_left_pct = fuzzy_left_pct
        self._fuzzy_width_pct = fuzzy_width_pct
        self._today_pct = today_pct
        self.update()

    def paintEvent(self, event: Any) -> None:
        """Paint the timeline visualization."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        track_y = h // 2 - 4
        track_height = 8

        # Background track
        painter.fillRect(0, track_y, w, track_height, Qt.GlobalColor.lightGray)

        # Spent (red) — cast all to int
        spent_width = int(w * self._spent_pct / 100.0)
        painter.fillRect(0, track_y, spent_width, track_height, Qt.GlobalColor.red)

        # Committed (amber/orange)
        committed_x = spent_width
        committed_width = int(w * self._committed_pct / 100.0)
        painter.fillRect(committed_x, track_y, committed_width, track_height, Qt.GlobalColor.yellow)

        # Fuzzy (light green)
        fuzzy_x = int(w * self._fuzzy_left_pct / 100.0)
        fuzzy_width = int(w * self._fuzzy_width_pct / 100.0)
        painter.fillRect(fuzzy_x, track_y, fuzzy_width, track_height, Qt.GlobalColor.green)

        # Today marker (black line)
        today_x = int(w * self._today_pct / 100.0)
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawLine(today_x, track_y - 4, today_x, track_y + track_height + 4)

        painter.end()


class MainWindow(QMainWindow):
    """
    Presentation-only main dashboard window.

    Displays balance snapshot, monthly stats, and upcoming/recent transactions.
    Emits signals for user actions (refresh, add income/spend/charge).
    No business logic, no repository access, no domain modifications.
    """

    # ── SIGNALS ──
    refresh_requested = pyqtSignal()
    add_income_requested = pyqtSignal()
    add_spend_requested = pyqtSignal()
    add_charge_requested = pyqtSignal()

    def __init__(self) -> None:
        """
        Initialize the presentation-only dashboard shell.

        :return: None.
        """
        super().__init__()
        self.setWindowTitle("Student Expense Tracker")
        self.setMinimumSize(1000, 680)

        # ── DISPLAY WIDGETS ──
        self._free_money_value = QLabel("₪0")
        self._state_value = QLabel("normal")
        self._monthly_budget_value = QLabel("₪0")
        self._monthly_spent_value = QLabel("₪0")
        self._monthly_left_value = QLabel("₪0")
        self._last_sync_label = QLabel("Never synced")

        # Timeline widget for visual feedback
        self._timeline_widget = TimelineWidget()

        self.setCentralWidget(self._build_central_widget())

    # ── PUBLIC SETTERS (for controller to call) ──

    def set_snapshot(self, snapshot: BalanceViewModel, last_sync: datetime | None = None, animate: bool = True) -> None:
        """
        Update dashboard display with a balance snapshot.

        :param snapshot: Formatted balance view model.
        :param last_sync: Last synchronization timestamp (optional).
        :param animate: Whether to animate the transition (ignored in this phase).
        :return: None.
        """
        self._free_money_value.setText(snapshot.free_money_str)
        self._state_value.setText(snapshot.balance_state_value)
        self._monthly_budget_value.setText(snapshot.monthly_budget_str)
        self._monthly_spent_value.setText(snapshot.monthly_spent_str)
        self._monthly_left_value.setText(snapshot.monthly_left_str)

        if last_sync:
            self._last_sync_label.setText(f"Last synced: {last_sync.strftime('%Y-%m-%d %H:%M')}")

        # Update timeline with percentages from snapshot
        self._timeline_widget.set_percentages(
            snapshot.timeline_spent_pct,
            snapshot.timeline_committed_pct,
            snapshot.timeline_fuzzy_left_pct,
            snapshot.timeline_fuzzy_width_pct,
            snapshot.today_pct,
        )

    def set_upcoming(self, charges: Iterable[Any]) -> None:
        """
        Update upcoming charges list (placeholder for now).

        :param charges: Iterable of upcoming charge items (format TBD).
        :return: None.
        """
        # TODO: implement charge list display when dialogs/list widgets are built
        pass

    def set_recent(self, transactions: Iterable[Any]) -> None:
        """
        Update recent transactions list (placeholder for now).

        :param transactions: Iterable of recent transaction items (format TBD).
        :return: None.
        """
        # TODO: implement transaction list display when dialogs/list widgets are built
        pass

    def set_categories(self, categories: Iterable[Any]) -> None:
        """
        Update category breakdown view (placeholder for now).

        :param categories: Iterable of category items (format TBD).
        :return: None.
        """
        # TODO: implement category breakdown when specialized widget is built
        pass

    def update_timeline(
        self,
        spent_pct: float,
        committed_pct: float,
        fuzzy_left_pct: float,
        fuzzy_width_pct: float,
        today_pct: float,
    ) -> None:
        """
        Update timeline visualization only (called separately or via set_snapshot).

        :param spent_pct: Percent of budget spent.
        :param committed_pct: Percent of budget committed.
        :param fuzzy_left_pct: Percent left in fuzzy range.
        :param fuzzy_width_pct: Width of fuzzy range.
        :param today_pct: Position of today marker.
        :return: None.
        """
        self._timeline_widget.set_percentages(spent_pct, committed_pct, fuzzy_left_pct, fuzzy_width_pct, today_pct)

    def set_last_sync(self, dt: datetime | None) -> None:
        """
        Update the last-sync label.

        :param dt: Synchronization timestamp or None.
        :return: None.
        """
        if dt:
            self._last_sync_label.setText(f"Last synced: {dt.strftime('%Y-%m-%d %H:%M')}")
        else:
            self._last_sync_label.setText("Never synced")

    # ── LAYOUT BUILDING (presentation only) ──

    def _build_central_widget(self) -> QWidget:
        """
        Build the dashboard layout.

        :return: Root dashboard widget.
        """
        root = QWidget()
        root.setObjectName("dashboardRoot")

        layout = QVBoxLayout(root)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        layout.addLayout(self._build_header())
        layout.addWidget(self._build_money_panel())
        layout.addWidget(self._timeline_widget)
        layout.addLayout(self._build_stat_row())
        layout.addLayout(self._build_detail_grid(), stretch=1)
        layout.addLayout(self._build_action_row())

        root.setStyleSheet(
            """
            QWidget#dashboardRoot {
                background: #f7f3ec;
                color: #17172b;
                font-family: Consolas, "Courier New", monospace;
            }
            QLabel#eyebrow {
                color: #747887;
                font-size: 11px;
                letter-spacing: 1px;
            }
            QLabel#title {
                font-size: 28px;
                font-weight: 700;
            }
            QFrame#card {
                background: #ffffff;
                border: 1px solid #ded7ca;
                border-radius: 8px;
            }
            QLabel#cardLabel {
                color: #747887;
                font-size: 11px;
            }
            QLabel#moneyValue {
                font-size: 54px;
                font-weight: 700;
            }
            QLabel#stateValue {
                background: #edf7f2;
                color: #1f6b52;
                border: 1px solid #b9decf;
                border-radius: 4px;
                padding: 4px 10px;
            }
            QLabel#statValue {
                font-size: 24px;
                font-weight: 700;
            }
            QPushButton {
                background: #17172b;
                color: #d0aa50;
                border: none;
                border-radius: 6px;
                padding: 9px 14px;
            }
            QPushButton:hover {
                background: #24243d;
            }
            """
        )
        return root

    def _build_header(self) -> QHBoxLayout:
        """
        Build the dashboard header row.

        :return: Header layout.
        """
        layout = QHBoxLayout()

        title_stack = QVBoxLayout()
        eyebrow = QLabel("Stage 2 / PyQt6")
        eyebrow.setObjectName("eyebrow")
        title = QLabel("Mizān Dashboard")
        title.setObjectName("title")
        title_stack.addWidget(eyebrow)
        title_stack.addWidget(title)

        layout.addLayout(title_stack)
        layout.addWidget(self._last_sync_label)
        layout.addStretch()

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(refresh_button)

        return layout

    def _build_money_panel(self) -> QFrame:
        """
        Build the main free-money panel.

        :return: Money panel widget.
        """
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(10)

        top_row = QHBoxLayout()
        label = QLabel("Free Money")
        label.setObjectName("cardLabel")
        self._state_value.setObjectName("stateValue")
        top_row.addWidget(label)
        top_row.addStretch()
        top_row.addWidget(self._state_value)

        self._free_money_value.setObjectName("moneyValue")
        subtitle = QLabel("after spend and committed charges")
        subtitle.setObjectName("cardLabel")

        layout.addLayout(top_row)
        layout.addWidget(self._free_money_value)
        layout.addWidget(subtitle)

        return card

    def _build_stat_row(self) -> QHBoxLayout:
        """
        Build the monthly summary row.

        :return: Stats' layout.
        """
        layout = QHBoxLayout()
        layout.setSpacing(14)
        layout.addWidget(self._build_stat_card("Monthly Budget", self._monthly_budget_value))
        layout.addWidget(self._build_stat_card("Monthly Spent", self._monthly_spent_value))
        layout.addWidget(self._build_stat_card("Monthly Left", self._monthly_left_value))
        return layout

    def _build_detail_grid(self) -> QGridLayout:
        """
        Build dashboard detail panels.

        :return: Detail grid layout.
        """
        layout = QGridLayout()
        layout.setSpacing(14)
        layout.addWidget(self._build_placeholder_panel("Upcoming Charges", "No upcoming charges loaded yet."), 0, 0)
        layout.addWidget(self._build_placeholder_panel("Recent Transactions", "No recent transactions loaded yet."), 0, 1)
        layout.addWidget(self._build_placeholder_panel("By Category", "Category breakdown will appear here."), 1, 0, 1, 2)
        return layout

    def _build_action_row(self) -> QHBoxLayout:
        """
        Build primary dashboard actions.

        :return: Action row layout.
        """
        layout = QHBoxLayout()
        layout.addStretch()

        add_income_btn = QPushButton("Add Income")
        add_income_btn.clicked.connect(self.add_income_requested.emit)
        layout.addWidget(add_income_btn)

        add_spend_btn = QPushButton("Add Spend")
        add_spend_btn.clicked.connect(self.add_spend_requested.emit)
        layout.addWidget(add_spend_btn)

        add_charge_btn = QPushButton("Add Charge")
        add_charge_btn.clicked.connect(self.add_charge_requested.emit)
        layout.addWidget(add_charge_btn)

        return layout

    def _build_stat_card(self, label_text: str, value_label: QLabel) -> QFrame:
        """
        Build one monthly stat card.

        :param label_text: Card label.
        :param value_label: Value widget controlled by the window.
        :return: Stat card widget.
        """
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)

        label = QLabel(label_text)
        label.setObjectName("cardLabel")
        value_label.setObjectName("statValue")

        layout.addWidget(label)
        layout.addWidget(value_label)
        layout.addStretch()
        return card

    def _build_placeholder_panel(self, title_text: str, empty_text: str) -> QFrame:
        """
        Build a placeholder panel for a future live list.

        :param title_text: Panel title.
        :param empty_text: Empty-state text.
        :return: Placeholder panel widget.
        """
        card = self._card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        title = QLabel(title_text)
        title.setObjectName("title")
        title.setStyleSheet("font-size: 16px;")

        empty = QLabel(empty_text)
        empty.setObjectName("cardLabel")
        empty.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(title)
        layout.addWidget(empty)
        layout.addStretch()
        return card

    @staticmethod
    def _card() -> QFrame:
        """
        Create a standard dashboard card frame.

        :return: Card frame.
        """
        card = QFrame()
        card.setObjectName("card")
        return card
