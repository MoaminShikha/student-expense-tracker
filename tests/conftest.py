from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from _pytest.terminal import TerminalReporter

# Add src/ to the path so all test subdirectories can import the package
# without requiring an editable install.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


class _ClassSeparatorPlugin:
    """Print module/class separators and a concise styled terminal summary."""

    def __init__(self, config: pytest.Config) -> None:
        self._config = config
        self._last_module: str | None = None
        self._last_class: str | None = None

    def pytest_runtest_logstart(self, nodeid: str, location: tuple[str, int | None, str]) -> None:
        parts = nodeid.split("::")
        current_module = parts[0] if parts else None
        current_class = parts[-2] if len(parts) >= 3 else None
        reporter: TerminalReporter | None = self._config.pluginmanager.get_plugin("terminalreporter")

        if reporter is None:
            return

        if current_module != self._last_module:
            self._last_module = current_module
            self._last_class = None
            reporter.write_line("")
            reporter.write_sep("=", current_module, bold=True, green=True)

        if current_class != self._last_class:
            self._last_class = current_class
            if current_class is not None:
                reporter.write_line("")
                reporter.write_sep("-", current_class, bold=True, cyan=True)

    def pytest_terminal_summary(self, terminalreporter: TerminalReporter, exitstatus: int, config: pytest.Config) -> None:
        passed = len(terminalreporter.stats.get("passed", []))
        failed = len(terminalreporter.stats.get("failed", []))
        skipped = len(terminalreporter.stats.get("skipped", []))
        errors = len(terminalreporter.stats.get("error", []))
        xfailed = len(terminalreporter.stats.get("xfailed", []))
        xpassed = len(terminalreporter.stats.get("xpassed", []))

        terminalreporter.write_line("")
        terminalreporter.write_sep("=", "Result Snapshot", bold=True, yellow=True)
        terminalreporter.write_line(f"passed={passed} failed={failed} errors={errors} skipped={skipped} xfailed={xfailed} xpassed={xpassed}", bold=True)


def pytest_configure(config: pytest.Config) -> None:
    config.pluginmanager.register(_ClassSeparatorPlugin(config))
