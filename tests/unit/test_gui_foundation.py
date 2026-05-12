from __future__ import annotations

import re


class TestTokens:
    """All color tokens must be valid hex strings."""

    def test_tokens_importable(self) -> None:
        from expense_tracker.app.gui.styles import tokens
        assert tokens is not None

    def _all_color_tokens(self) -> list[tuple[str, str]]:
        from expense_tracker.app.gui.styles import tokens
        return [
            (name, value)
            for name, value in vars(tokens).items()
            if isinstance(value, str) and not name.startswith("_")
            and name not in ("CATEGORY_COLORS",)
            and not any(c.islower() for c in name)
        ]

    def test_all_color_tokens_are_hex(self) -> None:
        hex_re = re.compile(r"^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?$")
        for name, value in self._all_color_tokens():
            assert hex_re.match(value), f"Token {name}={value!r} is not a valid hex color"

    def test_key_tokens_present(self) -> None:
        from expense_tracker.app.gui.styles.tokens import (
            BG, SURFACE, FG, MUTED, NAVY, GOLD, GOLD_LEAF,
            RED, GREEN, AMBER, HAIRLINE,
        )
        for token in [BG, SURFACE, FG, MUTED, NAVY, GOLD, GOLD_LEAF, RED, GREEN, AMBER, HAIRLINE]:
            assert isinstance(token, str)
            assert token.startswith("#")

    def test_category_colors_dict_has_all_categories(self) -> None:
        from expense_tracker.app.gui.styles.tokens import CATEGORY_COLORS
        for cat in ["food", "transport", "education", "entertainment", "other"]:
            assert cat in CATEGORY_COLORS
            assert CATEGORY_COLORS[cat].startswith("#")

    def test_layout_constants_are_positive_integers(self) -> None:
        from expense_tracker.app.gui.styles.tokens import (
            SIDEBAR_W, STAT_COL_W, CONTENT_PAD, CARD_RADIUS, TOPBAR_H,
        )
        for val in [SIDEBAR_W, STAT_COL_W, CONTENT_PAD, CARD_RADIUS, TOPBAR_H]:
            assert isinstance(val, int)
            assert val > 0


class TestFontsModule:
    """Font helpers must be importable and return the right types."""

    def test_fonts_module_importable(self) -> None:
        from expense_tracker.app.gui.styles import fonts
        assert fonts is not None

    def test_load_fonts_is_callable(self) -> None:
        from expense_tracker.app.gui.styles.fonts import load_fonts
        assert callable(load_fonts)

    def test_playfair_is_callable(self) -> None:
        from expense_tracker.app.gui.styles.fonts import playfair
        assert callable(playfair)

    def test_dm_mono_is_callable(self) -> None:
        from expense_tracker.app.gui.styles.fonts import dm_mono
        assert callable(dm_mono)

    def test_naskh_is_callable(self) -> None:
        from expense_tracker.app.gui.styles.fonts import naskh
        assert callable(naskh)

    def test_playfair_returns_qfont(self) -> None:
        import sys
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QFont
        app = QApplication.instance() or QApplication(sys.argv)
        from expense_tracker.app.gui.styles.fonts import playfair
        f = playfair(52, 900)
        assert isinstance(f, QFont)
        assert f.pointSize() == 52

    def test_dm_mono_returns_qfont(self) -> None:
        import sys
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QFont
        app = QApplication.instance() or QApplication(sys.argv)
        from expense_tracker.app.gui.styles.fonts import dm_mono
        f = dm_mono(11)
        assert isinstance(f, QFont)
        assert f.pointSize() == 11

    def test_naskh_returns_qfont(self) -> None:
        import sys
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QFont
        app = QApplication.instance() or QApplication(sys.argv)
        from expense_tracker.app.gui.styles.fonts import naskh
        f = naskh(25)
        assert isinstance(f, QFont)
        assert f.pointSize() == 25

    def test_load_fonts_is_idempotent(self) -> None:
        import sys
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication(sys.argv)
        from expense_tracker.app.gui.styles.fonts import load_fonts
        load_fonts()
        load_fonts()  # second call must not raise
