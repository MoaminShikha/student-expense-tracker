"""Add Charge dialog — collects name, amount, due date, optional recurring."""
from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal, InvalidOperation

from PyQt6.QtCore import QDate, QTimer, Qt
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

from expense_tracker.app.gui.styles.stylesheet import dialog_stylesheet
from expense_tracker.app.gui.widgets.error_dialog import ErrorDialog


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
        self.setStyleSheet(dialog_stylesheet())

        self.name:          str      = ""
        self.amount:        Decimal  = Decimal("0")
        self.due_date:      date     = date.today()
        self.is_recurring:  bool     = False
        self.day_of_month:  int      = 1
        self.reminder_days: int      = 3

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("e.g. Rent")
        self._name_edit.setMaxLength(100)
        self._name_edit.setAccessibleName("Charge name")
        self._name_edit.setAccessibleDescription("Enter a name for this charge, like Rent, Tuition, or Utilities")
        self._name_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._name_edit.setFocus()

        self._amount_edit = QLineEdit()
        self._amount_edit.setPlaceholderText("e.g. 400")
        self._amount_edit.setAccessibleName("Charge amount")
        self._amount_edit.setAccessibleDescription("Enter the amount in Israeli Shekels")
        self._amount_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDate(QDate.currentDate())
        self._date_edit.setDisplayFormat("dd MMM yyyy")
        self._date_edit.setAccessibleName("Due date")
        self._date_edit.setAccessibleDescription("Enter when this charge is due")
        self._date_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._recurring_cb = QCheckBox("Monthly recurring")
        self._recurring_cb.setAccessibleName("Monthly recurring")
        self._recurring_cb.setAccessibleDescription("Check this if the charge repeats every month")
        self._recurring_cb.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._recurring_cb.toggled.connect(self._on_recurring_toggled)

        self._day_spin = QSpinBox()
        self._day_spin.setRange(1, 31)
        self._day_spin.setValue(1)
        self._day_spin.setEnabled(False)
        self._day_spin.setAccessibleName("Day of month")
        self._day_spin.setAccessibleDescription("Enter which day of the month this charge repeats (1-28 recommended)")
        self._day_spin.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._reminder_spin = QSpinBox()
        self._reminder_spin.setRange(0, 30)
        self._reminder_spin.setValue(3)
        self._reminder_spin.setSuffix(" days")
        self._reminder_spin.setEnabled(False)
        self._reminder_spin.setAccessibleName("Reminder lead time")
        self._reminder_spin.setAccessibleDescription("Days before the charge is due to send a reminder")
        self._reminder_spin.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

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
        self._ok_btn.setText("&Add")
        self._ok_btn.setAccessibleName("Add charge")
        self._ok_btn.setAccessibleDescription("Click to add this charge (Alt+A)")
        self._ok_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_btn.setText("Cancel")
        cancel_btn.setAccessibleName("Cancel")
        cancel_btn.setAccessibleDescription("Click to cancel without adding")
        cancel_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

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
            ErrorDialog.show_error("Missing Name", "Please enter a charge name.", self)
            self._name_edit.setFocus()
            return

        raw = self._amount_edit.text().strip()
        try:
            amount = Decimal(raw)
            if amount <= 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            ErrorDialog.show_error("Invalid Amount", "Enter a positive number.", self)
            self._amount_edit.setFocus()
            self._amount_edit.selectAll()
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
