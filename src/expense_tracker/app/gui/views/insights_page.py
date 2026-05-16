from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QProgressBar,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.widgets.paper_widget import PaperWidget


class _KpiCard(QFrame):
    def __init__(self, title: str, value: str, accent: str = tokens.NAVY, subtitle: str = "") -> None:
        super().__init__()
        self.setObjectName("kpiCard")
        self.setStyleSheet(f"""
            QFrame#kpiCard {{
                background: {tokens.SURFACE};
                border: 1px solid {tokens.HAIRLINE};
                border-radius: 12px;
                border-top: 3px solid {accent};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 14)
        layout.setSpacing(4)

        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(f"font-size: {tokens.T_MICRO}px; letter-spacing: 2px; color: {tokens.MUTED}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")

        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"font-size: {tokens.T_XL}px; font-weight: 800; color: {accent}; font-family: 'Playfair Display'; background: transparent;")

        layout.addWidget(title_lbl)
        layout.addWidget(val_lbl)
        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet(f"font-size: {tokens.T_SM}px; color: {tokens.MUTED_FG}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
            layout.addWidget(sub)


class _BudgetProgress(QWidget):
    def __init__(self, label: str, pct: float, color: str = tokens.NAVY, sub: str = "") -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(4)

        row = QHBoxLayout()
        row.setSpacing(8)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size: {tokens.T_SM}px; font-weight: 700; color: {tokens.FG}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
        row.addWidget(lbl)
        if sub:
            sub_lbl = QLabel(sub)
            sub_lbl.setStyleSheet(f"font-size: {tokens.T_MICRO}px; color: {tokens.MUTED}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
            sub_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            row.addStretch()
            row.addWidget(sub_lbl)

        pct_lbl = QLabel(f"{pct:.0f}%")
        pct_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        pct_lbl.setFixedWidth(50)
        pct_lbl.setStyleSheet(f"font-size: {tokens.T_SM}px; font-weight: 700; color: {color}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
        row.addWidget(pct_lbl)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(int(min(pct, 100)))
        bar.setTextVisible(False)
        bar.setFixedHeight(8)
        bar.setStyleSheet(f"""
            QProgressBar {{
                background: {tokens.HAIRLINE};
                border-radius: 4px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color}, stop:1 {tokens.GOLD});
                border-radius: 4px;
            }}
        """)
        layout.addLayout(row)
        layout.addWidget(bar)


class _CategoryBar(QWidget):
    def __init__(self, name: str, amount_str: str, pct: float, color: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(3)

        row = QHBoxLayout()
        row.setSpacing(8)
        dot = QLabel("●")
        dot.setStyleSheet(f"font-size: 10px; color: {color}; background: transparent;")
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"font-size: {tokens.T_SM}px; color: {tokens.FG}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
        row.addWidget(dot)
        row.addWidget(name_lbl)
        row.addStretch()

        amt = QLabel(amount_str)
        amt.setStyleSheet(f"font-size: {tokens.T_SM}px; font-weight: 600; color: {tokens.NAVY}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
        row.addWidget(amt)

        pct_lbl = QLabel(f"{pct:.0f}%")
        pct_lbl.setFixedWidth(45)
        pct_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        pct_lbl.setStyleSheet(f"font-size: {tokens.T_SM}px; color: {tokens.MUTED}; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
        row.addWidget(pct_lbl)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(int(min(pct, 100)))
        bar.setTextVisible(False)
        bar.setFixedHeight(6)
        bar.setStyleSheet(f"""
            QProgressBar {{
                background: {tokens.HAIRLINE};
                border-radius: 3px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: {color};
                border-radius: 3px;
            }}
        """)
        layout.addLayout(row)
        layout.addWidget(bar)


class InsightsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("insightsPage")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background: {tokens.BG}; border: none; }}")
        self._content = PaperWidget()
        self._content.setObjectName("insightsContent")

        body = QVBoxLayout(self._content)
        body.setContentsMargins(32, 24, 32, 32)
        body.setSpacing(24)

        self._kpi_row = QHBoxLayout()
        self._kpi_row.setSpacing(16)
        for _ in range(4):
            card = _KpiCard("—", "—")
            self._kpi_row.addWidget(card)
        body.addLayout(self._kpi_row)

        self._tracking_section = QWidget()
        self._tracking_section.setObjectName("trackingSection")
        ts_layout = QVBoxLayout(self._tracking_section)
        ts_layout.setContentsMargins(0, 0, 0, 0)
        ts_layout.setSpacing(12)
        ts_header = QLabel("TRACKING")
        ts_header.setStyleSheet(f"font-size: {tokens.T_MICRO}px; letter-spacing: 3px; color: {tokens.MUTED}; font-family: 'DM Mono', Consolas, monospace; font-weight: 700; background: transparent;")
        ts_layout.addWidget(ts_header)
        self._util_progress = _BudgetProgress("Utilized", 0, tokens.NAVY)
        ts_layout.addWidget(self._util_progress)
        body.addWidget(self._tracking_section)

        self._daily_section = QWidget()
        self._daily_section.setObjectName("dailySection")
        ds_layout = QVBoxLayout(self._daily_section)
        ds_layout.setContentsMargins(0, 0, 0, 0)
        ds_layout.setSpacing(12)
        ds_header = QLabel("DAILY BURN")
        ds_header.setStyleSheet(f"font-size: {tokens.T_MICRO}px; letter-spacing: 3px; color: {tokens.MUTED}; font-family: 'DM Mono', Consolas, monospace; font-weight: 700; background: transparent;")
        ds_layout.addWidget(ds_header)
        self._daily_progress = _BudgetProgress("Burn vs Budget", 0, tokens.VIOLET)
        ds_layout.addWidget(self._daily_progress)
        body.addWidget(self._daily_section)

        self._encumbrance_section = QWidget()
        self._encumbrance_section.setObjectName("encumbranceSection")
        es_layout = QVBoxLayout(self._encumbrance_section)
        es_layout.setContentsMargins(0, 0, 0, 0)
        es_layout.setSpacing(12)
        es_header = QLabel("ENCUMBRANCE")
        es_header.setStyleSheet(f"font-size: {tokens.T_MICRO}px; letter-spacing: 3px; color: {tokens.MUTED}; font-family: 'DM Mono', Consolas, monospace; font-weight: 700; background: transparent;")
        es_layout.addWidget(es_header)
        self._encumbrance_progress = _BudgetProgress("Budget Allocation", 0, tokens.AMBER)
        es_layout.addWidget(self._encumbrance_progress)
        body.addWidget(self._encumbrance_section)

        self._cats_section = QWidget()
        self._cats_section.setObjectName("categorySection")
        cs_layout = QVBoxLayout(self._cats_section)
        cs_layout.setContentsMargins(0, 0, 0, 0)
        cs_layout.setSpacing(12)
        cs_header = QLabel("CATEGORY BREAKDOWN")
        cs_header.setStyleSheet(f"font-size: {tokens.T_MICRO}px; letter-spacing: 3px; color: {tokens.MUTED}; font-family: 'DM Mono', Consolas, monospace; font-weight: 700; background: transparent;")
        cs_layout.addWidget(cs_header)
        self._cat_container = QVBoxLayout()
        self._cat_container.setSpacing(4)
        cs_layout.addLayout(self._cat_container)
        body.addWidget(self._cats_section)

        body.addStretch()
        scroll.setWidget(self._content)
        outer.addWidget(scroll, stretch=1)

    def set_data(
        self,
        cat_bars: list[dict],
        cat_total_str: str,
        cat_budget_str: str,
        total_utilized_pct: float,
        daily_burn_str: str,
        daily_budget_str: str,
        daily_pct: float,
        runway_days: int,
        remaining_str: str,
        committed_str: str,
        fuzzy_str: str,
        available_str: str,
        available_pct: float,
        encumbered_pct: float,
        fuzzy_pct: float,
    ) -> None:
        self._update_kpis(daily_burn_str, remaining_str, committed_str, available_str, runway_days)
        self._util_progress = self._swap_progress(self._tracking_section, self._util_progress, f"Utilized {cat_total_str} / {cat_budget_str}", total_utilized_pct, tokens.NAVY)
        self._daily_progress = self._swap_progress(self._daily_section, self._daily_progress, f"Daily: {daily_burn_str} / {daily_budget_str}", daily_pct, tokens.VIOLET)
        self._encumbrance_progress = self._swap_progress(self._encumbrance_section, self._encumbrance_progress,
            f"Charges: {committed_str} · Fuzzy: {fuzzy_str} · Available: {available_str}",
            available_pct, tokens.AMBER, sub=f"Encumbered: {encumbered_pct:.0f}%  Fuzzy: {fuzzy_pct:.0f}%  Available: {available_pct:.0f}%")

        self._rebuild_cat_bars(cat_bars)

    def _update_kpis(self, daily_burn_str: str, remaining_str: str, committed_str: str, available_str: str, runway_days: int) -> None:
        cards_data = [
            ("Daily Burn", daily_burn_str, tokens.VIOLET, "avg spend per day"),
            ("Remaining", remaining_str, tokens.AMBER, "budget left this month"),
            ("Committed", committed_str, tokens.NAVY, "upcoming charges"),
            ("Available", available_str, tokens.GREEN, f"free money ({runway_days}d runway)"),
        ]
        self._recreate_kpi_cards(cards_data)

    def _recreate_kpi_cards(self, cards_data: list[tuple[str, str, str, str]]) -> None:
        while self._kpi_row.count():
            item = self._kpi_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for title, value, accent, subtitle in cards_data:
            self._kpi_row.addWidget(_KpiCard(title, value, accent, subtitle))

    def _swap_progress(self, parent: QWidget, old: _BudgetProgress | None, label: str, pct: float, color: str, sub: str = "") -> _BudgetProgress:
        if old is not None:
            old.setParent(None)
            old.deleteLater()
        new_w = _BudgetProgress(label, pct, color, sub)
        layout = parent.layout()
        if layout is not None:
            layout.insertWidget(layout.count(), new_w)
        return new_w

    def _rebuild_cat_bars(self, cat_bars: list[dict]) -> None:
        while self._cat_container.count():
            item = self._cat_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if not cat_bars:
            empty = QLabel("No spending this month.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(f"font-size: {tokens.T_SM}px; color: {tokens.MUTED}; padding: 16px; font-family: 'DM Mono', Consolas, monospace; background: transparent;")
            self._cat_container.addWidget(empty)
            return
        for cb in cat_bars:
            self._cat_container.addWidget(_CategoryBar(cb["name"], cb["amount_str"], cb["pct"], cb.get("color", tokens.NAVY)))
