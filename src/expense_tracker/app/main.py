from __future__ import annotations

from typing import Sequence


class ApplicationEntryPoint:
    """Bootstraps the command-line application."""

    def run(self, arguments: Sequence[str] | None = None) -> int:
        """
        Start the application lifecycle.

        :param arguments: Optional command-line arguments.
        :return: Process exit code.
        """
        pass


def main(arguments: Sequence[str] | None = None) -> int:
    """
    Execute the application entrypoint.

    :param arguments: Optional command-line arguments.
    :return: Process exit code.
    """
    pass


if __name__ == "__main__":
    raise SystemExit(main())


