"""Centralized QSS stylesheets for UI components."""

from . import tokens


def filter_pill_stylesheet(checked: bool = False) -> str:
    """Generate stylesheet for filter pill buttons."""
    return f"""
        QPushButton {{
            font-family: "DM Mono", Consolas, monospace;
            font-size: {tokens.T_XS}px;
            border: 1px solid {tokens.HAIRLINE};
            border-radius: 999px;
            padding: 4px 14px;
            background: transparent;
            color: {tokens.MUTED_FG};
        }}
        QPushButton:checked {{
            background: {tokens.NAVY};
            color: {tokens.GOLD};
            border-color: {tokens.NAVY};
            font-weight: 500;
        }}
        QPushButton:hover:!checked {{
            background: {tokens.PAPER_WARM};
        }}
    """


def ledger_date_label_stylesheet() -> str:
    """Generate stylesheet for ledger date labels."""
    return (
        f"font-size: {tokens.T_SM}px; color: {tokens.MUTED};"
        f"font-family: 'DM Mono', Consolas, monospace; background: transparent;"
    )


def ledger_description_label_stylesheet() -> str:
    """Generate stylesheet for ledger description labels."""
    return (
        f"font-size: {tokens.T_BASE}px; color: {tokens.FG};"
        f"font-family: 'DM Mono', Consolas, monospace; font-weight: 500; background: transparent;"
    )


def ledger_badge_stylesheet(foreground: str, background: str) -> str:
    """Generate stylesheet for ledger badge labels."""
    return (
        f"font-size: {tokens.T_SM}px; color: {foreground}; background: {background};"
        f"border-radius: 4px; font-weight: 700; font-family: 'DM Mono', Consolas, monospace;"
    )


def ledger_amount_label_stylesheet(color: str) -> str:
    """Generate stylesheet for ledger amount labels."""
    return (
        f"font-family: 'Playfair Display'; font-size: {tokens.T_MD}px;"
        f"font-weight: 700; color: {color}; background: transparent;"
    )


def ledger_balance_label_stylesheet() -> str:
    """Generate stylesheet for ledger balance labels."""
    return (
        f"font-family: 'Playfair Display'; font-size: {tokens.T_MD}px;"
        f"font-weight: 700; color: {tokens.FG}; background: transparent;"
    )


def application_stylesheet() -> str:
    """Generate global stylesheet for the application with accessibility improvements."""
    return f"""
        /* Global properties */
        QWidget {{
            background-color: {tokens.BG};
            color: {tokens.FG};
        }}

        QMainWindow {{
            background-color: {tokens.BG};
        }}

        /* Global focus indicators for keyboard navigation */
        QPushButton:focus {{
            outline: 1px solid {tokens.GOLD};
            outline-offset: 8px;
        }}

        QLineEdit:focus {{
            border: 1px solid {tokens.GOLD};
            outline: none;
            background-color: {tokens.SURFACE};
        }}

        QLineEdit {{
            border: 1px solid {tokens.HAIRLINE};
            border-radius: 4px;
            padding: 4px 8px;
            background-color: {tokens.SURFACE};
            color: {tokens.FG};
            selection-background-color: {tokens.GOLD};
        }}

        /* Scrollbar styling for dark mode */
        QScrollBar:vertical {{
            width: 10px;
            background-color: {tokens.BG};
        }}
        QScrollBar::handle:vertical {{
            background-color: {tokens.HAIRLINE};
            border-radius: 5px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {tokens.HAIRLINE_S};
        }}
    """
