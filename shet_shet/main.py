"""Application entry point."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from .ui import MainWindow


def _configure_logging() -> None:
    log_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ShetShetNakitaAko" / "logs"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=log_dir / "app.log", level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )
    except OSError:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


def main() -> int:
    _configure_logging()
    app = QApplication(sys.argv)
    app.setApplicationName("SHET SHET NAKITA AKO")
    app.setOrganizationName("ShetShetNakitaAko")
    try:
        window = MainWindow(Path(__file__).resolve().parent.parent)
        window.show()
        return app.exec()
    except Exception as exc:
        logging.exception("Application startup failed")
        QMessageBox.critical(None, "Could not start", f"The application could not start.\n\n{exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
