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
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui.styles.stylesheet import dialog_stylesheet
from expense_tracker.app.gui.widgets.error_dialog import ErrorDialog
from expense_tracker.domain.models.income import IncomeSourceTag

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
        self.setStyleSheet(dialog_stylesheet())

        # Result fields (set on accept)
        self.amount:     Decimal            = Decimal("0")
        self.source_tag: IncomeSourceTag    = IncomeSourceTag.OTHER
        self.entry_date: date               = date.today()

        # ── Form ──────────────────────────────────────────────────────────────
        self._amount_edit = QLineEdit()
        self._amount_edit.setPlaceholderText("e.g. 500")
        self._amount_edit.setAccessibleName("Income amount")
        self._amount_edit.setAccessibleDescription("Enter the amount of income in Israeli Shekels")
        self._amount_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._amount_edit.setFocus()

        self._source_combo = QComboBox()
        for label in _SOURCE_LABELS:
            self._source_combo.addItem(label)
        self._source_combo.setCurrentText("Other")
        self._source_combo.setAccessibleName("Income source")
        self._source_combo.setAccessibleDescription("Select where the income came from: Scholarship, Family, Work, or Other")
        self._source_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDate(QDate.currentDate())
        self._date_edit.setDisplayFormat("dd MMM yyyy")
        self._date_edit.setAccessibleName("Income date")
        self._date_edit.setAccessibleDescription("Enter the date this income was received")
        self._date_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("Amount (₪)", self._amount_edit)
        form.addRow("Source",     self._source_combo)
        form.addRow("Date",       self._date_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self._ok_btn.setText("&Add")
        self._ok_btn.setAccessibleName("Add income")
        self._ok_btn.setAccessibleDescription("Click to add this income entry (Alt+A)")
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
            ErrorDialog.show_error("Invalid Amount", "Enter a positive number (e.g. 500).", self)
            self._amount_edit.setFocus()
            self._amount_edit.selectAll()
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
