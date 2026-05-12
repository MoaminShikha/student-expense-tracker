from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

# Ensure src/ is in path for direct execution (pytest handles this via conftest.py)
_src_path = Path(__file__).resolve().parent.parent.parent.parent / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from .controllers.dashboard_controller import DashboardController
from .views.main_window import MainWindow


def main() -> int:
    """
    Start the PyQt6 desktop application.

    Bootstrap QApplication, create MainWindow and controller scaffold.
    Services are optional and None at startup (will be wired in later stages).

    :return: Process exit code.
    """
    try:
        app = QApplication(sys.argv)
        window = MainWindow()

        # Wire controller to view (services are None in scaffold phase)
        controller = DashboardController(view=window)

        window.show()
        return app.exec()
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

