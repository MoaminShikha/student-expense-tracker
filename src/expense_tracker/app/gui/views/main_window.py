from __future__ import annotations

from collections.abc import Iterable
import calendar
from datetime import datetime
from typing import TYPE_CHECKING, Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QPalette
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.styles.textures import dot_grain
from expense_tracker.app.gui.widgets.footer_strip import FooterStrip
from expense_tracker.app.gui.widgets.heads_up_alert import HeadsUpAlert
from expense_tracker.app.gui.widgets.hero_card import HeroCard
from expense_tracker.app.gui.widgets.panels import CategoryPanel, ChargeRowVM, RecentPanel, TxRowVM, UpcomingPanel, CategoryRowVM
from expense_tracker.app.gui.widgets.sidebar import Sidebar
from expense_tracker.app.gui.widgets.stat_column import StatColumn
from expense_tracker.app.gui.widgets.timeline_widget import TimelineWidget
from expense_tracker.app.gui.widgets.topbar import Topbar


class PaperWidget(QWidget):
    """
    Scroll-content background: solid BG fill + dot-grain texture overlay.
    Matches the HTML body::before radial-gradient dot pattern.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(dot_grain()))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

if TYPE_CHECKING:
    from expense_tracker.app.gui.view_models.balance_view_model import BalanceViewModel


class MainWindow(QMainWindow):
    """
    Presentation-only main dashboard window.

    Two-column layout: Sidebar (fixed) + Main area (topbar + scrollable content).
    Emits signals for user actions — no business logic, no repository access.
    """

    # ── SIGNALS ───────────────────────────────────────────────────────────────
    refresh_requested    = pyqtSignal()
    add_income_requested = pyqtSignal()
    add_spend_requested  = pyqtSignal()
    add_charge_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Mizān")
        self.setMinimumSize(1100, 720)

        # Sub-widgets
        self._sidebar     = Sidebar()
        self._topbar      = Topbar()
        self._stat_column = StatColumn()
        self._hero        = HeroCard()

        # Heads-up alert strip
        self._alert = HeadsUpAlert()

        # Bottom panels
        self._cat_panel      = CategoryPanel(self.add_income_requested)
        self._upcoming_panel = UpcomingPanel(self.add_charge_requested)
        self._recent_panel   = RecentPanel(self.add_spend_requested)

        # Footer
        self._footer = FooterStrip()

        # Wire topbar sync button → window signal
        self._topbar.refresh_requested.connect(self.refresh_requested.emit)

        self.setCentralWidget(self._build_root())

    # ── PUBLIC SETTERS ─────────────────────────────────────────────────────────

    def set_snapshot(
        self,
        snapshot: BalanceViewModel,
        last_sync: datetime | None = None,
        animate: bool = True,
    ) -> None:
        """Push a balance snapshot into the view."""
        self._hero.set_money(snapshot.free_money_str)
        self._hero.set_state(snapshot.balance_state_value)
        self._hero.set_period_for_today()
        self._hero.set_legend(
            snapshot.monthly_spent_str,
            "₪0",
            "₪0",
            snapshot.monthly_budget_str,
        )
        self._hero.set_today_changes(f"TODAY  ·  Monthly left {snapshot.monthly_left_str}")
        self._hero.timeline.set_percentages(
            snapshot.timeline_spent_pct,
            snapshot.timeline_committed_pct,
            snapshot.timeline_fuzzy_left_pct,
            snapshot.timeline_fuzzy_width_pct,
            snapshot.today_pct,
        )
        today = datetime.now().date()
        last_day = calendar.monthrange(today.year, today.month)[1]
        self._hero.timeline.set_ticks([(100.0, "Rent")])
        self._hero.timeline.set_endpoints("Limit", f"Rent · {last_day} {today.strftime('%b')}")

        if last_sync:
            self._topbar.set_last_sync(last_sync.strftime("%d %b · %H:%M"))

        self._topbar.set_on_track_state(snapshot.on_track_state_value)
        self._stat_column.set_snapshot(snapshot)

    def set_upcoming(self, rows: Iterable[ChargeRowVM]) -> None:
        self._upcoming_panel.set_upcoming(list(rows))

    def set_recent(self, rows: Iterable[TxRowVM]) -> None:
        self._recent_panel.set_recent(list(rows))

    def set_categories(self, rows: Iterable[CategoryRowVM]) -> None:
        self._cat_panel.set_categories(list(rows))

    def update_timeline(
        self,
        spent_pct: float,
        committed_pct: float,
        fuzzy_left_pct: float,
        fuzzy_width_pct: float,
        today_pct: float,
    ) -> None:
        self._hero.timeline.set_percentages(
            spent_pct, committed_pct, fuzzy_left_pct, fuzzy_width_pct, today_pct
        )

    def set_last_sync(self, dt: datetime | None) -> None:
        if dt:
            self._topbar.set_last_sync(dt.strftime("%d %b · %H:%M"))

    def set_alert(self, body_html: str, amount_str: str, visible: bool) -> None:
        """Show or hide the heads-up alert strip with the given content."""
        self._alert.set_data(body_html, amount_str)
        self._alert.set_visible(visible)

    # ── ROOT LAYOUT ───────────────────────────────────────────────────────────

    def _build_root(self) -> QWidget:
        """Two-column root: Sidebar | Main area."""
        root = QWidget()
        root.setObjectName("appRoot")

        h = QHBoxLayout(root)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        h.addWidget(self._sidebar)
        h.addWidget(self._build_main_area(), stretch=1)

        root.setStyleSheet(f"""
            QWidget#appRoot {{
                background: {tokens.BG};
            }}
        """)
        return root

    def _build_main_area(self) -> QWidget:
        """Topbar + scrollable content."""
        w = QWidget()
        w.setObjectName("mainArea")

        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        # Topbar
        v.addWidget(self._topbar)

        # Hairline divider below topbar
        divider = QFrame()
        divider.setObjectName("topbarDivider")
        divider.setFixedHeight(1)
        v.addWidget(divider)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(self._build_content())
        v.addWidget(scroll, stretch=1)

        w.setStyleSheet(f"""
            QWidget#mainArea {{
                background: {tokens.BG};
            }}
            QFrame#topbarDivider {{
                background: {tokens.HAIRLINE};
            }}
            QScrollArea {{
                background: {tokens.BG};
                border: none;
            }}
            QWidget#contentRoot {{
                background: transparent;
            }}
        """)
        return w

    def _build_content(self) -> QWidget:
        """Scrollable content: hero row + panels + footer."""
        w = PaperWidget()
        w.setObjectName("contentRoot")

        layout = QVBoxLayout(w)
        layout.setContentsMargins(
            tokens.CONTENT_PAD, 18,
            tokens.CONTENT_PAD, 18,
        )
        layout.setSpacing(14)

        # Alert strip (hidden by default, shown when a charge is due soon)
        layout.addWidget(self._alert)

        # Hero row: hero card (stretch) + stat column (fixed)
        # Must use a container widget so child QFrames get a C++ parent
        hero_container = QWidget()
        hero_row = QHBoxLayout(hero_container)
        hero_row.setContentsMargins(0, 0, 0, 0)
        hero_row.setSpacing(12)
        hero_row.addWidget(self._hero, stretch=1)
        hero_row.addWidget(self._stat_column)
        layout.addWidget(hero_container)

        # Panels row: 3 equal columns
        layout.addWidget(self._build_panels_row())

        # Footer
        layout.addWidget(self._footer)

        # Apply content-level styles — background is transparent so PaperWidget shows through
        w.setStyleSheet(f"""
            QWidget#contentRoot {{
                background: transparent;
                font-family: "DM Mono", Consolas, monospace;
            }}
            QFrame#card {{
                background: {tokens.SURFACE};
                border: 1px solid {tokens.HAIRLINE};
                border-radius: {tokens.CARD_RADIUS}px;
            }}
            QLabel#cardMicro {{
                font-size: {tokens.T_MINI}px;
                letter-spacing: 2px;
                color: {tokens.MUTED};
                background: transparent;
            }}
            QLabel#cardSubtitle {{
                font-size: {tokens.T_SM}px;
                color: {tokens.MUTED};
                background: transparent;
            }}
            QLabel#moneyValue {{
                font-size: 54px;
                font-weight: 900;
                font-family: "Playfair Display";
                color: {tokens.FG};
                background: transparent;
            }}
            QLabel#panelTitle {{
                font-size: {tokens.T_BASE}px;
                font-weight: 500;
                color: {tokens.FG};
                background: transparent;
            }}
            QLabel#emptyState {{
                font-size: {tokens.T_SM}px;
                color: {tokens.MUTED};
                background: transparent;
            }}
            QLabel#footerText {{
                font-size: {tokens.T_MINI}px;
                letter-spacing: 1px;
                color: {tokens.MUTED};
                background: transparent;
            }}
            QPushButton#actionBtn {{
                font-family: "DM Mono", Consolas, monospace;
                font-size: {tokens.T_SM}px;
                font-weight: 500;
                background: {tokens.NAVY};
                color: {tokens.GOLD};
                border: none;
                border-radius: 6px;
                padding: 9px 16px;
                letter-spacing: 1px;
            }}
            QPushButton#actionBtn:hover {{
                background: {tokens.FG};
            }}
        """)
        return w

    # Hero card is self._hero (HeroCard instance, built in __init__)

    # ── PANELS ────────────────────────────────────────────────────────────────

    def _build_panels_row(self) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(self._cat_panel,      stretch=1)
        layout.addWidget(self._upcoming_panel, stretch=1)
        layout.addWidget(self._recent_panel,   stretch=1)
        return w

    # Footer is self._footer (FooterStrip instance, built in __init__)
