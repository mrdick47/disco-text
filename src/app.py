import logging
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from src.gui.main_window import MainWindow
from src.gui.styles import STYLESHEET

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def main():
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_DIR / "disco-text.log", mode="w"),
        ],
    )
    logger = logging.getLogger("disco-text")
    logger.info("Starting Disco-Text")

    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough,
        )
        app = QApplication(sys.argv)
        app.setStyleSheet(STYLESHEET)
        app.setApplicationName("Disco-Text")
        app.setOrganizationName("Disco-Text")

        logger.info("Creating main window")
        window = MainWindow()
        logger.info("Showing main window")
        window.show()
        logger.info("Entering event loop")
        ret = app.exec()
        logger.info("Event loop exited with code %s", ret)
        sys.exit(ret)
    except Exception:
        logger.exception("Fatal error in main")
        sys.exit(1)


if __name__ == "__main__":
    main()
