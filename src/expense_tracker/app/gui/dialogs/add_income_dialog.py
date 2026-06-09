"""Add Income dialog — collects amount, source tag, date."""
from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation

from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui.styles import tokens
from expense_tracker.domain.models.income import IncomeSourceTag

_DIALOG_SS = f"""
    QDialog {{
        background: {tokens.SURFACE};
        font-family: "DM Mono", Consolas, monospace;
    }}
    QLabel {{
        font-size: {tokens.T_SM}px;
        color: {tokens.FG};
        background: transparent;
    }}
    QLineEdit, QComboBox, QDateEdit {{
        border: 1px solid {tokens.HAIRLINE};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: {tokens.T_SM}px;
        font-family: "DM Mono", Consolas, monospace;
        color: {tokens.FG};
        background: {tokens.SURFACE};
    }}
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
        border: 1px solid {tokens.GOLD};
    }}
    QComboBox QAbstractItemView {{
        background: {tokens.SURFACE};
        color: {tokens.FG};
        selection-background-color: {tokens.PAPER_WARM};
        selection-color: {tokens.FG};
        border: 1px solid {tokens.HAIRLINE};
    }}
    QDialogButtonBox QPushButton {{
        font-family: "DM Mono", Consolas, monospace;
        font-size: {tokens.T_SM}px;
        padding: 7px 18px;
        border-radius: 6px;
    }}
    QDialogButtonBox QPushButton[text="Add"] {{
        background: {tokens.NAVY};
        color: {tokens.GOLD};
        border: none;
    }}
    QDialogButtonBox QPushButton[text="Add"]:hover {{
        background: {tokens.FG};
    }}
    QDialogButtonBox QPushButton[text="Cancel"] {{
        background: transparent;
        border: 1px solid {tokens.HAIRLINE};
        color: {tokens.MUTED_FG};
    }}
"""

_SOURCE_LABELS = {
    "Scholarship": IncomeSourceTag.SCHOLARSHIP,
    "Family":      IncomeSourceTag.FAMILY,
    "Work":        IncomeSourceTag.WORK,
    "Other":       IncomeSourceTag.OTHER,
}


class AddIncomeDialog(QDialog):
    """
    Modal dialog to add one income entry.
    On accept, exposes .amount, .source_tag, .entry_date.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Income")
        self.setMinimumWidth(340)
        self.setStyleSheet(_DIALOG_SS)

        # Result fields (set on accept)
        self.amount:     Decimal            = Decimal("0")
        self.source_tag: IncomeSourceTag    = IncomeSourceTag.OTHER
        self.entry_date: date               = date.today()

        # ── Form ──────────────────────────────────────────────────────────────
        self._amount_edit = QLineEdit()
        self._amount_edit.setPlaceholderText("e.g. 500")
        self._amount_edit.setFocus()

        self._source_combo = QComboBox()
        for label in _SOURCE_LABELS:
            self._source_combo.addItem(label)
        self._source_combo.setCurrentText("Other")

        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDate(QDate.currentDate())
        self._date_edit.setDisplayFormat("dd MMM yyyy")

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("Amount (₪)", self._amount_edit)
        form.addRow("Source",     self._source_combo)
        form.addRow("Date",       self._date_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self._ok_btn.setText("Add")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel")
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        # Progress bar (hidden by default)
        self._progress = QProgressBar()
        self._progress.setMaximum(0)
        self._progress.setVisible(False)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.addLayout(form)
        layout.addWidget(self._progress)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        raw = self._amount_edit.text().strip()
        try:
            amount = Decimal(raw)
            if amount <= 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            QMessageBox.warning(self, "Invalid amount", "Enter a positive number (e.g. 500).")
            return

        # Show loading state
        self._progress.setVisible(True)
        self._ok_btn.setEnabled(False)
        self.repaint()

        # Simulate processing delay
        QTimer.singleShot(200, self._complete_accept)

    def _complete_accept(self) -> None:
        raw = self._amount_edit.text().strip()
        amount = Decimal(raw)

        self.amount     = amount
        self.source_tag = _SOURCE_LABELS[self._source_combo.currentText()]
        qd              = self._date_edit.date()
        self.entry_date = date(qd.year(), qd.month(), qd.day())
        self.accept()
