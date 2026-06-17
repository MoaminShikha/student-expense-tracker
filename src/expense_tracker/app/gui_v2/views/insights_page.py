from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from expense_tracker.app.gui_v2 import tokens


class InsightsPage(QWidget):
    """Insights page — delegates to the existing gui/ InsightsPage content."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("insightsPage")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(tokens.CONTENT_PAD, tokens.CONTENT_PAD, tokens.CONTENT_PAD, tokens.CONTENT_PAD)

        title = QLabel("Insights")
        title.setStyleSheet(
            f"font-family: 'Playfair Display'; font-size: {tokens.T_XL}px; font-weight: 700;"
            f"color: {tokens.FG}; background: transparent;"
        )
        placeholder = QLabel("Category breakdown, burn rate, and encumbrance charts will appear here.")
        placeholder.setWordWrap(True)
        placeholder.setStyleSheet(
            f"font-size: {tokens.T_SM}px; color: {tokens.MUTED};"
            "font-family: 'DM Mono', Consolas, monospace; background: transparent;"
        )
        layout.addWidget(title)
        layout.addWidget(placeholder)
        layout.addStretch()

        self.setStyleSheet(f"QWidget#insightsPage {{ background: {tokens.BG}; }}")

    # The gui/ InsightsPage content is wired by InsightsController; this view
    # acts as the mount point.  Controllers call set_* methods which will be
    # added here as the controller is connected.
