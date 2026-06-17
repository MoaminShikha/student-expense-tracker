from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from expense_tracker.app.gui_v2 import tokens


def _row(key: str, value: str) -> QWidget:
    w = QWidget()
    layout = QHBoxLayout(w)
    layout.setContentsMargins(0, 8, 0, 8)
    layout.setSpacing(0)
    k_lbl = QLabel(key)
    k_lbl.setStyleSheet(
        f"font-size: {tokens.T_SM}px; color: {tokens.MUTED};"
        "font-family: 'DM Mono', Consolas, monospace; background: transparent;"
    )
    v_lbl = QLabel(value)
    v_lbl.setStyleSheet(
        f"font-size: {tokens.T_SM}px; color: {tokens.FG};"
        "font-family: 'DM Mono', Consolas, monospace; background: transparent;"
    )
    layout.addWidget(k_lbl)
    layout.addStretch()
    layout.addWidget(v_lbl)
    return w


def _section(title: str) -> QLabel:
    lbl = QLabel(title)
    lbl.setStyleSheet(
        f"font-size: {tokens.T_MICRO}px; letter-spacing: 3px; color: {tokens.MUTED};"
        "font-family: 'DM Mono', Consolas, monospace; background: transparent; padding-top: 18px;"
    )
    return lbl


class SettingsPage(QWidget):
    """Minimal settings page: data directory path, app version, and session info."""

    def __init__(self, data_dir: Path | None = None, version: str = "2.0.0") -> None:
        super().__init__()
        self.setObjectName("settingsPage")
        self._data_dir = data_dir
        self._version = version
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(tokens.CONTENT_PAD, tokens.CONTENT_PAD, tokens.CONTENT_PAD, tokens.CONTENT_PAD)
        layout.setSpacing(0)

        title = QLabel("Settings")
        title.setStyleSheet(
            f"font-family: 'Playfair Display'; font-size: {tokens.T_XL}px; font-weight: 700;"
            f"color: {tokens.FG}; background: transparent;"
        )
        layout.addWidget(title)

        card = QFrame()
        card.setObjectName("settingsCard")
        card.setStyleSheet(f"""
            QFrame#settingsCard {{
                background: {tokens.SURFACE}; border: 1px solid {tokens.HAIRLINE};
                border-radius: {tokens.CARD_RADIUS}px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(0)

        card_layout.addWidget(_section("APPLICATION"))
        card_layout.addWidget(self._divider())
        card_layout.addWidget(_row("Version", self._version))
        card_layout.addWidget(_row("GUI", "v2 — experimental"))
        card_layout.addWidget(self._divider())
        card_layout.addWidget(_section("DATA"))
        card_layout.addWidget(self._divider())
        data_path = str(self._data_dir) if self._data_dir else "—"
        card_layout.addWidget(_row("Data directory", data_path))
        card_layout.addWidget(self._divider())
        card_layout.addWidget(_section("SUPPORT"))
        card_layout.addWidget(self._divider())
        card_layout.addWidget(_row("Report issues", "github.com / expense-tracker"))

        layout.addSpacing(tokens.SPACE_LG)
        layout.addWidget(card)
        layout.addStretch()

        self.setStyleSheet(f"QWidget#settingsPage {{ background: {tokens.BG}; }}")

    def _divider(self) -> QFrame:
        d = QFrame()
        d.setFixedHeight(1)
        d.setStyleSheet(f"background: {tokens.HAIRLINE}; border: none;")
        return d
