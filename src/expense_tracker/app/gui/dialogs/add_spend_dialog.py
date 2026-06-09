"""Add Spend dialog — collects amount, description, category, date."""
from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation

from PyQt6.QtCore import QDate, QTimer, Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui.styles.stylesheet import dialog_stylesheet
from expense_tracker.app.gui.widgets.error_dialog import ErrorDialog
from expense_tracker.domain.models.transaction import TransactionCategory

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
        self.setStyleSheet(dialog_stylesheet())

        self.amount:      Decimal                  = Decimal("0")
        self.description: str                      = ""
        self.category:    TransactionCategory | None = TransactionCategory.OTHER
        self.spent_on:    date                     = date.today()

        self._amount_edit = QLineEdit()
        self._amount_edit.setPlaceholderText("e.g. 45")
        self._amount_edit.setAccessibleName("Spend amount")
        self._amount_edit.setAccessibleDescription("Enter how much you spent in Israeli Shekels")
        self._amount_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._amount_edit.setFocus()

        self._desc_edit = QLineEdit()
        self._desc_edit.setPlaceholderText("e.g. Lunch at campus")
        self._desc_edit.setMaxLength(500)
        self._desc_edit.setAccessibleName("Description")
        self._desc_edit.setAccessibleDescription("Describe what you spent money on (e.g., Lunch, Coffee, Transport)")
        self._desc_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._cat_combo = QComboBox()
        for label in _CAT_LABELS:
            self._cat_combo.addItem(label)
        self._cat_combo.setCurrentText("Other")
        self._cat_combo.setAccessibleName("Category")
        self._cat_combo.setAccessibleDescription("Select the category: Food, Transport, Education, Entertainment, or Other")
        self._cat_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDate(QDate.currentDate())
        self._date_edit.setDisplayFormat("dd MMM yyyy")
        self._date_edit.setAccessibleName("Spend date")
        self._date_edit.setAccessibleDescription("Enter the date you made this purchase")
        self._date_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("Amount (₪)",   self._amount_edit)
        form.addRow("Description",  self._desc_edit)
        form.addRow("Category",     self._cat_combo)
        form.addRow("Date",         self._date_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self._ok_btn.setText("&Add")
        self._ok_btn.setAccessibleName("Add spend")
        self._ok_btn.setAccessibleDescription("Click to add this spending entry (Alt+A)")
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

    def _on_accept(self) -> None:
        raw = self._amount_edit.text().strip()
        try:
            amount = Decimal(raw)
            if amount <= 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            ErrorDialog.show_error("Invalid Amount", "Enter a positive number (e.g. 45).", self)
            self._amount_edit.setFocus()
            self._amount_edit.selectAll()
            return

        desc = self._desc_edit.text().strip()
        if not desc:
            ErrorDialog.show_error("Missing Description", "Please enter a description.", self)
            self._desc_edit.setFocus()
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
        desc = self._desc_edit.text().strip()

        self.amount      = amount
        self.description = desc
        self.category    = _CAT_LABELS[self._cat_combo.currentText()]
        qd               = self._date_edit.date()
        self.spent_on    = date(qd.year(), qd.month(), qd.day())
        self.accept()
