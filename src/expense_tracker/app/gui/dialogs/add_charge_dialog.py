"""Add Charge dialog — collects name, amount, due date, optional recurring."""
from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal, InvalidOperation

from PyQt6.QtCore import QDate, QTimer
from PyQt6.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui.styles import tokens

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
    QLineEdit, QComboBox, QDateEdit, QSpinBox {{
        border: 1px solid {tokens.HAIRLINE};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: {tokens.T_SM}px;
        font-family: "DM Mono", Consolas, monospace;
        color: {tokens.FG};
        background: {tokens.SURFACE};
    }}
    QLineEdit:focus, QDateEdit:focus, QSpinBox:focus {{
        border: 1px solid {tokens.GOLD};
    }}
    QCheckBox {{
        font-size: {tokens.T_SM}px;
        color: {tokens.FG};
        background: transparent;
        spacing: 6px;
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


class AddChargeDialog(QDialog):
    """
    Modal dialog to add a committed charge (one-off or recurring).

    On accept exposes:
        .name, .amount, .due_date      — always set
        .is_recurring                  — bool
        .day_of_month, .reminder_days  — only valid when is_recurring=True
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Charge")
        self.setMinimumWidth(360)
        self.setStyleSheet(_DIALOG_SS)

        self.name:          str      = ""
        self.amount:        Decimal  = Decimal("0")
        self.due_date:      date     = date.today()
        self.is_recurring:  bool     = False
        self.day_of_month:  int      = 1
        self.reminder_days: int      = 3

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("e.g. Rent")
        self._name_edit.setMaxLength(100)
        self._name_edit.setFocus()

        self._amount_edit = QLineEdit()
        self._amount_edit.setPlaceholderText("e.g. 400")

        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDate(QDate.currentDate())
        self._date_edit.setDisplayFormat("dd MMM yyyy")

        self._recurring_cb = QCheckBox("Monthly recurring")
        self._recurring_cb.toggled.connect(self._on_recurring_toggled)

        self._day_spin = QSpinBox()
        self._day_spin.setRange(1, 31)
        self._day_spin.setValue(1)
        self._day_spin.setEnabled(False)

        self._reminder_spin = QSpinBox()
        self._reminder_spin.setRange(0, 30)
        self._reminder_spin.setValue(3)
        self._reminder_spin.setSuffix(" days")
        self._reminder_spin.setEnabled(False)

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("Name",           self._name_edit)
        form.addRow("Amount (₪)",     self._amount_edit)
        form.addRow("Due date",       self._date_edit)
        form.addRow("",               self._recurring_cb)
        self._day_row_lbl = QLabel("Day of month")
        form.addRow(self._day_row_lbl, self._day_spin)
        self._reminder_row_lbl = QLabel("Reminder lead time")
        form.addRow(self._reminder_row_lbl, self._reminder_spin)
        self._day_row_lbl.setVisible(False)
        self._reminder_row_lbl.setVisible(False)
        self._day_spin.setVisible(False)
        self._reminder_spin.setVisible(False)

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

    def _on_recurring_toggled(self, checked: bool) -> None:
        self._day_spin.setEnabled(checked)
        self._reminder_spin.setEnabled(checked)
        self._day_row_lbl.setVisible(checked)
        self._reminder_row_lbl.setVisible(checked)
        self._day_spin.setVisible(checked)
        self._reminder_spin.setVisible(checked)
        self.adjustSize()

    def _on_accept(self) -> None:
        name = self._name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing name", "Please enter a charge name.")
            return

        raw = self._amount_edit.text().strip()
        try:
            amount = Decimal(raw)
            if amount <= 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            QMessageBox.warning(self, "Invalid amount", "Enter a positive number.")
            return

        day_of_month = self._day_spin.value()
        if self._recurring_cb.isChecked():
            if day_of_month > 28:
                QMessageBox.warning(
                    self,
                    "Invalid day",
                    "For monthly recurring, use day 1-28 (to avoid Feb/Apr/Jun/Sep/Nov issues)."
                )
                return

        # Show loading state
        self._progress.setVisible(True)
        self._ok_btn.setEnabled(False)
        self.repaint()

        # Simulate processing delay
        QTimer.singleShot(200, self._complete_accept)

    def _complete_accept(self) -> None:
        name = self._name_edit.text().strip()
        raw = self._amount_edit.text().strip()
        amount = Decimal(raw)
        day_of_month = self._day_spin.value()

        self.name          = name
        self.amount        = amount
        self.is_recurring  = self._recurring_cb.isChecked()
        self.day_of_month  = day_of_month
        self.reminder_days = self._reminder_spin.value()
        qd                 = self._date_edit.date()
        self.due_date      = date(qd.year(), qd.month(), qd.day())
        self.accept()
