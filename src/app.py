import logging
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from src.gui.main_window import MainWindow
from src.gui.styles import STYLESHEET
from src.version import get_version

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def main():
    LOG_DIR.mkdir(exist_ok=True)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)

    file_handler = logging.FileHandler(LOG_DIR / "disco-text.log", mode="w")
    file_handler.setLevel(logging.DEBUG)

    logging.basicConfig(
        level=logging.WARNING,
        format=LOG_FORMAT,
        handlers=[console_handler, file_handler],
    )
    logger = logging.getLogger("disco-text")
    logger.setLevel(logging.DEBUG)
    discoord_logger = logging.getLogger("discord")
    discoord_logger.setLevel(logging.WARNING)

    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough,
        )
        app = QApplication(sys.argv)
        app.setStyleSheet(STYLESHEET)
        app.setApplicationName("Disco-Text")
        app.setOrganizationName("Disco-Text")
        app.setApplicationVersion(get_version())

        icon_path = Path(__file__).resolve().parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))

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
