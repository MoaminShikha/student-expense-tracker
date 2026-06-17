from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRectF, Qt, pyqtProperty  # type: ignore[attr-defined]
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui_v2 import tokens


# ── Row view-models ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class CategoryRowVM:
    """View model for a single row in the By Category breakdown panel."""

    name: str
    key: str
    amount_str: str
    pct: float


@dataclass(frozen=True)
class ChargeRowVM:
    """View model for a single row in the Upcoming Charges panel."""

    name: str
    amount_str: str
    due_str: str
    relative_str: str
    recurring: bool


@dataclass(frozen=True)
class TxRowVM:
    """View model for a single row in the Recent Transactions panel."""

    name: str
    category_key: str
    place: str
    amount_str: str
    timestamp_str: str


# ── Base panel ────────────────────────────────────────────────────────────────

class _Panel(QFrame):
    """Base card panel with header + scrollable body and a 280 ms fade-up on first show."""

    def __init__(self, title: str, btn_text: str, btn_signal, meta: str = "") -> None:
        super().__init__()
        self.setObjectName("panelCard")
        self.setMinimumHeight(200)
        self.setStyleSheet(f"""
            QFrame#panelCard {{
                background: {tokens.SURFACE};
                border: 1px solid {tokens.HAIRLINE};
                border-radius: {tokens.PANEL_RADIUS}px;
            }}
        """)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 16, 18, 16)
        outer.setSpacing(10)
        head = QHBoxLayout()
        head.setContentsMargins(0, 0, 0, 0)
        head.setSpacing(5)
        marker = QFrame()
        marker.setFixedSize(4, 4)
        marker.setStyleSheet(f"background: {tokens.GOLD}; border: none;")
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            f"font-size: {tokens.T_SM}px; color: {tokens.FG}; font-weight: 500;"
            "font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        btn = QPushButton(btn_text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none; color: {tokens.GOLD_LEAF};
                font-size: {tokens.T_SM}px; font-family: "DM Mono", Consolas, monospace;
                padding: 2px 4px;
            }}
            QPushButton:hover {{ text-decoration: underline; }}
        """)
        btn.clicked.connect(btn_signal.emit)
        head.addWidget(marker, alignment=Qt.AlignmentFlag.AlignVCenter)
        head.addWidget(title_lbl)
        head.addStretch()
        head.addWidget(btn)
        self._meta_lbl = QLabel(meta)
        self._meta_lbl.setStyleSheet(
            f"font-size: {tokens.T_SM}px; color: {tokens.MUTED};"
            "font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        self._meta_lbl.setVisible(bool(meta))
        hdr_w = QWidget()
        hdr_l = QVBoxLayout(hdr_w)
        hdr_l.setContentsMargins(0, 0, 0, 0)
        hdr_l.setSpacing(1)
        hdr_l.addLayout(head)
        hdr_l.addWidget(self._meta_lbl)
        outer.addWidget(hdr_w)
        self._body = QVBoxLayout()
        self._body.setContentsMargins(0, 0, 0, 0)
        self._body.setSpacing(0)
        outer.addLayout(self._body, stretch=1)
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)
        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._fade_anim.setDuration(280)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animated = False

    def set_meta(self, text: str) -> None:
        self._meta_lbl.setText(text)
        self._meta_lbl.setVisible(bool(text))

    def showEvent(self, event: Any) -> None:
        super().showEvent(event)
        if not self._animated:
            self._animated = True
            self._fade_anim.start()

    def _clear_body(self) -> None:
        while self._body.count():
            item = self._body.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _empty_state(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
        lbl.setStyleSheet(
            f"font-size: {tokens.T_SM}px; color: {tokens.MUTED};"
            "font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        lbl.setWordWrap(True)
        return lbl


class CategoryPanel(_Panel):
    """By Category panel with color-coded progress bar rows."""

    def __init__(self, btn_signal) -> None:
        from datetime import date
        super().__init__("By Category", "Details →", btn_signal,
                         meta=f"{date.today().strftime('%B')} · month-to-date")
        self._body.addWidget(self._empty_state("Category breakdown will appear here."))

    def set_categories(self, rows: list[CategoryRowVM]) -> None:
        self._clear_body()
        if not rows:
            self._body.addWidget(self._empty_state("No spend data yet."))
            return
        for row in rows:
            color = tokens.CATEGORY_COLORS.get(row.key, tokens.MUTED)
            self._body.addWidget(self._cat_row(row, color))
        from decimal import Decimal
        total_raw = sum(
            Decimal(r.amount_str.replace("₪", "").replace(",", ""))
            for r in rows if r.amount_str
        )
        total_str = f"₪{total_raw:,.0f}" if total_raw else ""
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {tokens.HAIRLINE}; border: none;")
        self._body.addWidget(sep)
        footer_w = QWidget()
        footer_l = QHBoxLayout(footer_w)
        footer_l.setContentsMargins(0, 6, 0, 0)
        footer_l.setSpacing(0)
        lbl = QLabel("Total spent")
        lbl.setStyleSheet(f"font-size: {tokens.T_SM}px; color: {tokens.MUTED}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
        amt = QLabel(total_str)
        amt.setStyleSheet(f"font-family: 'Playfair Display'; font-size: {tokens.T_MD}px; font-weight: 700; color: {tokens.FG}; background: transparent;")
        footer_l.addWidget(lbl)
        footer_l.addStretch()
        footer_l.addWidget(amt)
        self._body.addWidget(footer_w)
        self._body.addStretch()

    def _cat_row(self, row: CategoryRowVM, color: str) -> QWidget:
        w = QWidget()
        vl = QVBoxLayout(w)
        vl.setContentsMargins(4, 2, 4, 4)
        vl.setSpacing(4)
        top = QHBoxLayout()
        dot = QFrame()
        dot.setFixedSize(7, 7)
        dot.setStyleSheet(f"background: {color}; border-radius: 3px; border: none;")
        name_lbl = QLabel(row.name.capitalize())
        name_lbl.setStyleSheet(f"font-size: {tokens.T_BASE}px; color: {tokens.FG}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
        pct_lbl = QLabel(f"{row.pct:.0f}%")
        pct_lbl.setStyleSheet(f"font-size: {tokens.T_SM}px; color: {tokens.MUTED}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
        amt_lbl = QLabel(row.amount_str)
        amt_lbl.setStyleSheet(f"font-family: 'Playfair Display'; font-size: {tokens.T_MD}px; font-weight: 700; color: {tokens.FG}; background: transparent;")
        top.addWidget(dot, alignment=Qt.AlignmentFlag.AlignVCenter)
        top.addSpacing(7)
        top.addWidget(name_lbl)
        top.addWidget(pct_lbl)
        top.addStretch()
        top.addWidget(amt_lbl)
        bar_track = QFrame()
        bar_track.setFixedHeight(5)
        bar_track.setStyleSheet(f"background: {tokens.TRACK}; border-radius: 3px; border: none;")
        bar_inner = QHBoxLayout(bar_track)
        bar_inner.setContentsMargins(0, 0, 0, 0)
        bar_inner.setSpacing(0)
        fill_pct = max(0.0, min(100.0, row.pct))
        bar_fill_w = QWidget()
        bar_fill_w.setStyleSheet(f"background: {color}; border-radius: 3px;")
        bar_inner.addWidget(bar_fill_w, stretch=int(fill_pct))
        bar_inner.addStretch(max(1, int(100 - fill_pct)))
        vl.addLayout(top)
        vl.addWidget(bar_track)
        return w


class UpcomingPanel(_Panel):
    """Upcoming Charges panel with urgency-colored rows."""

    def __init__(self, btn_signal) -> None:
        super().__init__("Upcoming", "+ Add Charge", btn_signal, meta="charges due soon")
        self._body.addWidget(self._empty_state("No upcoming charges loaded yet."))

    def set_upcoming(self, rows: list[ChargeRowVM]) -> None:
        count = len(rows)
        self.set_meta(f"{count} charge{'s' if count != 1 else ''} due soon" if rows else "charges due soon")
        self._clear_body()
        if not rows:
            self._body.addWidget(self._empty_state("No upcoming charges."))
            return
        for i, row in enumerate(rows):
            self._body.addWidget(self._charge_row(row, first=(i == 0), last=(i == len(rows) - 1)))
        self._body.addStretch()

    def _charge_row(self, row: ChargeRowVM, first: bool, last: bool) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 9 if not first else 0, 0, 9 if not last else 0)
        layout.setSpacing(11)
        stripe = QFrame()
        stripe.setFixedWidth(4)
        stripe.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        stripe.setMinimumHeight(28)
        stripe.setStyleSheet(f"background: {tokens.RED}; border-radius: 999px; border: none;")
        body_w = QWidget()
        body_l = QVBoxLayout(body_w)
        body_l.setContentsMargins(0, 0, 0, 0)
        body_l.setSpacing(1)
        name_row = QHBoxLayout()
        name_lbl = QLabel(row.name)
        name_lbl.setStyleSheet(f"font-size: {tokens.T_BASE}px; color: {tokens.FG}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
        name_row.addWidget(name_lbl)
        if row.recurring:
            rec = QLabel("↻")
            rec.setStyleSheet(f"font-size: {tokens.T_XS}px; color: {tokens.MUTED}; background: transparent;")
            name_row.addWidget(rec)
        name_row.addStretch()
        date_lbl = QLabel(row.due_str)
        date_lbl.setStyleSheet(f"font-size: {tokens.T_SM}px; color: {tokens.MUTED}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
        body_l.addLayout(name_row)
        body_l.addWidget(date_lbl)
        right_w = QWidget()
        right_l = QVBoxLayout(right_w)
        right_l.setContentsMargins(0, 0, 0, 0)
        right_l.setSpacing(1)
        amt = QLabel(row.amount_str)
        amt.setAlignment(Qt.AlignmentFlag.AlignRight)
        amt.setStyleSheet(f"font-family: 'Playfair Display'; font-size: {tokens.T_MD}px; font-weight: 700; color: {tokens.RED}; background: transparent;")
        timing = QLabel(row.relative_str)
        timing.setAlignment(Qt.AlignmentFlag.AlignRight)
        timing.setStyleSheet(f"font-size: {tokens.T_SM}px; color: {tokens.MUTED}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
        right_l.addWidget(amt)
        right_l.addWidget(timing)
        layout.addWidget(stripe)
        layout.addWidget(body_w, stretch=1)
        layout.addWidget(right_w)
        if not last:
            container = QWidget()
            cl = QVBoxLayout(container)
            cl.setContentsMargins(0, 0, 0, 0)
            cl.setSpacing(0)
            cl.addWidget(w)
            sep = QFrame()
            sep.setFixedHeight(1)
            sep.setStyleSheet(f"background: {tokens.HAIRLINE}; border: none;")
            cl.addWidget(sep)
            return container
        return w


class RecentPanel(_Panel):
    """Recent Transactions panel."""

    def __init__(self, btn_signal) -> None:
        super().__init__("Recent", "+ Add Spend", btn_signal, meta="last entries")
        self._body.addWidget(self._empty_state("No recent transactions loaded yet."))

    def set_recent(self, rows: list[TxRowVM]) -> None:
        count = len(rows)
        self.set_meta(f"Last {count} {'entry' if count == 1 else 'entries'}" if rows else "last entries")
        self._clear_body()
        if not rows:
            self._body.addWidget(self._empty_state("No transactions yet."))
            return
        for i, row in enumerate(rows):
            self._body.addWidget(self._tx_row(row, last=(i == len(rows) - 1)))
        self._body.addStretch()

    def _tx_row(self, row: TxRowVM, last: bool) -> QWidget:
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 8, 0, 8 if not last else 0)
        layout.setSpacing(10)
        color = tokens.CATEGORY_COLORS.get(row.category_key, tokens.MUTED)
        icon = _CategoryIcon(color)
        body_w = QWidget()
        body_l = QVBoxLayout(body_w)
        body_l.setContentsMargins(0, 0, 0, 0)
        body_l.setSpacing(1)
        name_lbl = QLabel(row.name)
        name_lbl.setStyleSheet(f"font-size: {tokens.T_SM}px; color: {tokens.FG}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
        name_lbl.setMaximumWidth(160)
        meta_lbl = QLabel(f"{row.category_key.capitalize()} · {row.place}" if row.place else row.category_key.capitalize())
        meta_lbl.setStyleSheet(f"font-size: {tokens.T_SM}px; color: {tokens.MUTED}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
        body_l.addWidget(name_lbl)
        body_l.addWidget(meta_lbl)
        right_w = QWidget()
        right_l = QVBoxLayout(right_w)
        right_l.setContentsMargins(0, 0, 0, 0)
        right_l.setSpacing(1)
        amt = QLabel(row.amount_str)
        amt.setAlignment(Qt.AlignmentFlag.AlignRight)
        amt.setStyleSheet(f"font-family: 'Playfair Display'; font-size: {tokens.T_MD}px; font-weight: 700; color: {tokens.FG}; background: transparent;")
        time_lbl = QLabel(row.timestamp_str)
        time_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        time_lbl.setStyleSheet(f"font-size: {tokens.T_MINI}px; color: {tokens.MUTED}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
        right_l.addWidget(amt)
        right_l.addWidget(time_lbl)
        layout.addWidget(icon)
        layout.addWidget(body_w, stretch=1)
        layout.addWidget(right_w)
        if not last:
            container = QWidget()
            cl = QVBoxLayout(container)
            cl.setContentsMargins(0, 0, 0, 0)
            cl.setSpacing(0)
            cl.addWidget(w)
            sep = QFrame()
            sep.setFixedHeight(1)
            sep.setStyleSheet(f"background: {tokens.HAIRLINE}; border: none;")
            cl.addWidget(sep)
            return container
        return w


class _CategoryIcon(QWidget):
    """30×30 rounded square with category-color border."""

    def __init__(self, color_hex: str) -> None:
        super().__init__()
        self.setFixedSize(30, 30)
        self._color = QColor(color_hex)

    def paintEvent(self, _event: Any) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg = QColor(self._color)
        bg.setAlpha(30)
        p.setPen(self._color)
        p.setBrush(bg)
        p.drawRoundedRect(QRectF(0.5, 0.5, 29, 29), 8, 8)
        p.end()
