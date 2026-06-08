"""Add Spend dialog — collects amount, description, category, date."""
from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui.styles import tokens
from expense_tracker.app.gui.widgets.error_dialog import ErrorDialog
from expense_tracker.domain.models.transaction import TransactionCategory

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

_CAT_LABELS = {
    "Food":          TransactionCategory.FOOD,
    "Transport":     TransactionCategory.TRANSPORT,
    "Education":     TransactionCategory.EDUCATION,
    "Entertainment": TransactionCategory.ENTERTAINMENT,
    "Other":         TransactionCategory.OTHER,
}


class AddSpendDialog(QDialog):
    """
    Modal dialog to add one spend transaction.
    On accept, exposes .amount, .description, .category, .spent_on.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Spend")
        self.setMinimumWidth(340)
        self.setStyleSheet(_DIALOG_SS)

        self.amount:      Decimal                  = Decimal("0")
        self.description: str                      = ""
        self.category:    TransactionCategory | None = TransactionCategory.OTHER
        self.spent_on:    date                     = date.today()

        self._amount_edit = QLineEdit()
        self._amount_edit.setPlaceholderText("e.g. 45")

        self._desc_edit = QLineEdit()
        self._desc_edit.setPlaceholderText("e.g. Lunch at campus")

        self._cat_combo = QComboBox()
        for label in _CAT_LABELS:
            self._cat_combo.addItem(label)
        self._cat_combo.setCurrentText("Other")

        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDate(QDate.currentDate())
        self._date_edit.setDisplayFormat("dd MMM yyyy")

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("Amount (₪)",   self._amount_edit)
        form.addRow("Description",  self._desc_edit)
        form.addRow("Category",     self._cat_combo)
        form.addRow("Date",         self._date_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Add")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel")
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        raw = self._amount_edit.text().strip()
        try:
            amount = Decimal(raw)
            if amount <= 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            ErrorDialog.show_error("Invalid Amount", "Enter a positive number (e.g. 45).", self)
            return

        desc = self._desc_edit.text().strip()
        if not desc:
            ErrorDialog.show_error("Missing Description", "Please enter a description.", self)
            return

        self.amount      = amount
        self.description = desc
        self.category    = _CAT_LABELS[self._cat_combo.currentText()]
        qd               = self._date_edit.date()
        self.spent_on    = date(qd.year(), qd.month(), qd.day())
        self.accept()
