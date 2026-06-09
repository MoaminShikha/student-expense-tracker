"""Theme manager for light/dark mode switching."""
from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal
from expense_tracker.app.gui.styles import tokens


class ThemeManager(QObject):
    """Manages theme switching between light and dark modes."""

    theme_changed = pyqtSignal(str)  # emits "light" or "dark"

    def __init__(self) -> None:
        super().__init__()
        self._theme = "dark"  # Start with dark mode enabled by default
        self._color_map = {}
        self._setup_color_map()

    def _setup_color_map(self) -> None:
        """Map light tokens to their dark equivalents."""
        self._color_map = {
            tokens.BG: (tokens.BG, tokens.DARK_BG),
            tokens.PAPER_WARM: (tokens.PAPER_WARM, tokens.DARK_PAPER_WARM),
            tokens.SURFACE: (tokens.SURFACE, tokens.DARK_SURFACE),
            tokens.HAIRLINE: (tokens.HAIRLINE, tokens.DARK_HAIRLINE),
            tokens.HAIRLINE_S: (tokens.HAIRLINE_S, tokens.DARK_HAIRLINE_S),
            tokens.FG: (tokens.FG, tokens.DARK_FG),
            tokens.MUTED_FG: (tokens.MUTED_FG, tokens.DARK_MUTED_FG),
            tokens.MUTED: (tokens.MUTED, tokens.DARK_MUTED),
            tokens.DISABLED: (tokens.DISABLED, tokens.DARK_DISABLED),
            tokens.RED: (tokens.RED, tokens.DARK_RED),
            tokens.GREEN: (tokens.GREEN, tokens.DARK_GREEN),
            tokens.GOLD: (tokens.GOLD, tokens.DARK_GOLD),
            tokens.AMBER: (tokens.AMBER, tokens.DARK_AMBER),
        }

    def set_theme(self, theme: str) -> None:
        """Switch to light or dark theme."""
        if theme not in ("light", "dark"):
            return
        self._theme = theme
        self.theme_changed.emit(theme)
        # Apply stylesheet changes
        self._apply_stylesheet()

    def get_color(self, light_color: str) -> str:
        """Get the appropriate color for current theme."""
        if self._theme == "light":
            return light_color
        if light_color in self._color_map:
            return self._color_map[light_color][1]
        return light_color

    @property
    def current_theme(self) -> str:
        """Get current theme ('light' or 'dark')."""
        return self._theme

    def is_dark(self) -> bool:
        """Check if dark mode is enabled."""
        return self._theme == "dark"

    def _apply_stylesheet(self) -> None:
        """Apply stylesheet changes to the application."""
        try:
            from PyQt6.QtWidgets import QApplication
            from expense_tracker.app.gui.styles.stylesheet_manager import apply_stylesheet
            app = QApplication.instance()
            if app:
                apply_stylesheet(app, self._theme)
        except Exception:
            pass  # Silently fail if stylesheet can't be applied


# Global theme manager instance
_theme_manager: ThemeManager | None = None


def get_theme_manager() -> ThemeManager:
    """Get or create the global theme manager."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
