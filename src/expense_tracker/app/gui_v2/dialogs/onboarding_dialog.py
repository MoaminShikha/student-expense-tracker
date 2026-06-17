from __future__ import annotations

from decimal import Decimal, InvalidOperation

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from expense_tracker.app.gui_v2 import tokens

_SS = f"""
    QDialog {{
        background: {tokens.SURFACE};
        font-family: "DM Mono", Consolas, monospace;
    }}
    QLabel {{
        font-size: {tokens.T_SM}px; color: {tokens.FG}; background: transparent;
    }}
    QLabel#onbTitle {{
        font-family: "Playfair Display"; font-size: {tokens.T_XL}px; font-weight: 700;
        color: {tokens.FG}; background: transparent;
    }}
    QLabel#onbSub {{
        font-size: {tokens.T_SM}px; color: {tokens.MUTED};
        font-family: "DM Mono", Consolas, monospace; background: transparent;
    }}
    QLabel#onbWordmark {{
        font-family: "Noto Naskh Arabic"; font-size: 28px; font-weight: 700;
        color: {tokens.GOLD}; background: transparent;
    }}
    QLineEdit {{
        border: 2px solid {tokens.HAIRLINE}; border-radius: 6px; padding: 8px 12px;
        font-size: {tokens.T_SM}px; font-family: "DM Mono", Consolas, monospace;
        color: {tokens.FG}; background: {tokens.BG};
    }}
    QLineEdit:focus {{ border: 2px solid {tokens.FOCUS}; }}
    QDialogButtonBox QPushButton {{
        font-family: "DM Mono", Consolas, monospace; font-size: {tokens.T_SM}px;
        padding: 8px 20px; border-radius: 6px;
    }}
    QDialogButtonBox QPushButton[text="Get started"] {{
        background: {tokens.NAVY}; color: {tokens.GOLD}; border: none; font-weight: 600;
    }}
    QDialogButtonBox QPushButton[text="Get started"]:hover {{ background: {tokens.FG}; }}
"""


class OnboardingDialog(QDialog):
    """First-run dialog: prompts the user for their opening monthly balance.

    Shows the ميزان wordmark and a brief tagline before the input.
    Exposes .opening_balance (Decimal) on accept.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Welcome to ميزان")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setMinimumWidth(400)
        self.setStyleSheet(_SS)

        self.opening_balance: Decimal = Decimal("0")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 24)
        layout.setSpacing(0)

        wordmark = QLabel("ميزان")
        wordmark.setObjectName("onbWordmark")
        wordmark.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(wordmark)
        layout.addSpacing(16)

        title = QLabel("Set your opening balance")
        title.setObjectName("onbTitle")
        layout.addWidget(title)
        layout.addSpacing(6)

        sub = QLabel(
            "Enter how much money you're starting this month with.\n"
            "You can update it later in Settings."
        )
        sub.setObjectName("onbSub")
        sub.setWordWrap(True)
        layout.addWidget(sub)
        layout.addSpacing(22)

        self._amount_edit = QLineEdit()
        self._amount_edit.setPlaceholderText("e.g. 2000")
        self._amount_edit.setFocus()

        form = QFormLayout()
        form.setSpacing(10)
        form.addRow("Opening balance (₪)", self._amount_edit)
        layout.addLayout(form)
        layout.addSpacing(24)

        buttons = QDialogButtonBox()
        self._ok_btn = buttons.addButton("Get started", QDialogButtonBox.ButtonRole.AcceptRole)
        buttons.accepted.connect(self._on_accept)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        raw = self._amount_edit.text().strip()
        try:
            amount = Decimal(raw)
            if amount < 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            QMessageBox.warning(self, "Invalid amount", "Enter zero or a positive number.")
            return
        self.opening_balance = amount
        self.accept()
