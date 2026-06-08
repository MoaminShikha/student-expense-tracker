"""Custom error dialog using app design system."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
)

from expense_tracker.app.gui.styles import tokens


class ErrorDialog(QDialog):
    """Custom error dialog styled with app design tokens."""

    def __init__(self, title: str, message: str, parent: QWidget | None = None) -> None:
        """
        Initialize error dialog.

        :param title: Dialog title
        :param message: Error message text
        :param parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setStyleSheet(f"background-color: {tokens.BG};")
        self._build_ui(title, message)

    def _build_ui(self, title: str, message: str) -> None:
        """Build dialog UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"font-size: {tokens.T_LG}px; font-weight: 700; color: {tokens.DANGER}; "
            f"font-family: 'DM Mono', Consolas, monospace;"
        )
        layout.addWidget(title_label)

        # Message
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(
            f"font-size: {tokens.T_BASE}px; color: {tokens.FG}; "
            f"font-family: 'DM Mono', Consolas, monospace; line-height: 1.5;"
        )
        layout.addWidget(msg_label)

        layout.addStretch()

        # OK button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_button = QPushButton("OK")
        ok_button.setFixedWidth(100)
        ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {tokens.NAVY};
                color: {tokens.GOLD};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-family: 'DM Mono', Consolas, monospace;
                font-size: {tokens.T_SM}px;
                font-weight: 500;
                cursor: pointer;
            }}
            QPushButton:hover {{
                background-color: {tokens.NAVY};
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                opacity: 0.8;
            }}
        """)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    @staticmethod
    def show_error(title: str, message: str, parent: QWidget | None = None) -> None:
        """
        Show error dialog and wait for user to close it.

        :param title: Error title
        :param message: Error message
        :param parent: Parent widget
        """
        dialog = ErrorDialog(title, message, parent)
        dialog.exec()
