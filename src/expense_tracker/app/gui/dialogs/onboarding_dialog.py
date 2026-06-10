"""Onboarding dialog — collects the opening balance to start the first session."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui.styles.stylesheet import dialog_stylesheet
from expense_tracker.app.gui.widgets.error_dialog import ErrorDialog


class OnboardingDialog(QDialog):
    """
    Modal first-run dialog that collects the session's opening balance.

    On accept, exposes ``.opening_balance``. Shown when no active session
    exists so the rest of the app has a session to attach income/charges to.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Welcome to Mizān")
        self.setMinimumWidth(360)
        self.setStyleSheet(dialog_stylesheet())

        # Result field (set on accept)
        self.opening_balance: Decimal = Decimal("0")

        intro = QLabel(
            "Let's set up your budget. Enter the current balance in your "
            "account — everything is tracked against this starting point."
        )
        intro.setWordWrap(True)

        self._amount_edit = QLineEdit()
        self._amount_edit.setPlaceholderText("e.g. 3200")
        self._amount_edit.setAccessibleName("Opening balance")
        self._amount_edit.setAccessibleDescription(
            "Enter your current account balance in Israeli Shekels"
        )
        self._amount_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._amount_edit.setFocus()

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("Opening balance (₪)", self._amount_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self._ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self._ok_btn.setText("&Start")
        self._ok_btn.setAccessibleName("Start budgeting")
        self._ok_btn.setAccessibleDescription("Create your session and open the app (Alt+S)")
        self._ok_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        buttons.accepted.connect(self._on_accept)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.addWidget(intro)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        raw = self._amount_edit.text().strip()
        try:
            amount = Decimal(raw)
            if amount < 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            ErrorDialog.show_error(
                "Invalid Balance", "Enter a number that is zero or greater (e.g. 3200).", self
            )
            self._amount_edit.setFocus()
            self._amount_edit.selectAll()
            return

        self.opening_balance = amount
        self.accept()
