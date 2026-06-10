import asyncio
import json
import logging
from pathlib import Path

import discord
from PyQt6.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from src.discord_client import DiscordClient
from src.gui.channel_panel import ChannelListPanel
from src.gui.export_dialog import ExportDialog
from src.gui.message_preview import MessagePreviewPanel
from src.gui.onboarding_dialog import OnboardingWizard
from src.gui.server_panel import ServerListPanel

logger = logging.getLogger(__name__)

CONFIG_DIR = Path.home() / ".disco-text"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def _save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


class _Bridge(QObject):
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error = pyqtSignal(str)


class _Signals:
    def __init__(self, bridge: _Bridge):
        self._bridge = bridge

    def on_connected(self) -> None:
        self._bridge.connected.emit()

    def on_disconnected(self) -> None:
        self._bridge.disconnected.emit()

    def on_error(self, message: str) -> None:
        self._bridge.error.emit(message)


class _ConnectWorker(QThread):
    connected = pyqtSignal()

    def __init__(self, client: DiscordClient, token: str):
        super().__init__()
        self._client = client
        self._token = token

    def run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._client.connect(self._token))
        except Exception:
            logger.exception("Connect worker error")
        finally:
            loop.close()


class _FetchWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, client: DiscordClient, channel_id: int):
        super().__init__()
        self._client = client
        self._channel_id = channel_id

    def _on_progress(self, count: int) -> None:
        self.progress.emit(count)

    def run(self) -> None:
        loop = self._client.get_loop()
        if loop is None:
            self.error.emit("Not connected to Discord")
            return
        future = asyncio.run_coroutine_threadsafe(
            self._client.fetch_messages(
                self._channel_id, progress_callback=self._on_progress
            ),
            loop,
        )
        try:
            messages = future.result(timeout=300)
            self.finished.emit(messages)
        except Exception as e:
            logger.exception("Fetch worker error")
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("MainWindow __init__ start")
        self.setWindowTitle("Disco-Text")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)

        self._client = DiscordClient()
        self._current_guild_id: str | None = None
        self._current_channel_id: str | None = None
        self._current_messages: list[discord.Message] = []
        self._connect_worker: _ConnectWorker | None = None
        self._bridge = _Bridge()
        self._bridge.connected.connect(self._on_connected)
        self._bridge.disconnected.connect(self._on_disconnected)
        self._bridge.error.connect(self._on_error)

        logger.info("Setting up UI")
        self._setup_ui()
        logger.info("UI setup done, loading token")
        self._load_token()
        logger.info("Token loaded")

        cfg = _load_config()
        if not cfg.get("onboarded"):
            logger.info("First run, showing onboarding wizard")
            self._show_onboarding()
        logger.info("MainWindow __init__ complete")

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        token_bar = QHBoxLayout()
        token_label = QLabel("Bot Token:")
        self._token_input = QLineEdit()
        self._token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._token_input.setPlaceholderText("Enter your Discord bot token...")
        self._token_input.returnPressed.connect(self._connect)
        token_bar.addWidget(token_label)
        token_bar.addWidget(self._token_input, 1)

        self._connect_btn = QPushButton("Connect")
        self._connect_btn.clicked.connect(self._connect)
        token_bar.addWidget(self._connect_btn)

        self._disconnect_btn = QPushButton("Disconnect")
        self._disconnect_btn.setObjectName("secondary")
        self._disconnect_btn.clicked.connect(self._disconnect)
        self._disconnect_btn.setEnabled(False)
        token_bar.addWidget(self._disconnect_btn)

        self._status_indicator = QLabel("● Disconnected")
        main_layout.addLayout(token_bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self._server_panel = ServerListPanel()
        self._server_panel.server_selected.connect(self._on_server_selected)
        splitter.addWidget(self._server_panel)

        self._channel_panel = ChannelListPanel()
        self._channel_panel.channel_selected.connect(self._on_channel_selected)
        splitter.addWidget(self._channel_panel)

        self._message_panel = MessagePreviewPanel()
        self._message_panel.selection_changed.connect(self._on_message_selection_changed)
        splitter.addWidget(self._message_panel)

        splitter.setSizes([200, 200, 500])
        main_layout.addWidget(splitter, 1)

        export_bar = QHBoxLayout()
        self._export_btn = QPushButton("Export Messages...")
        self._export_btn.setEnabled(False)
        self._export_btn.clicked.connect(self._show_export_dialog)
        self._export_selected_btn = QPushButton("Export Selected")
        self._export_selected_btn.setObjectName("secondary")
        self._export_selected_btn.setEnabled(False)
        self._export_selected_btn.clicked.connect(self._show_export_selected_dialog)
        export_bar.addWidget(self._export_btn)
        export_bar.addWidget(self._export_selected_btn)
        export_bar.addStretch()
        main_layout.addLayout(export_bar)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        onboard_action = file_menu.addAction("Setup Wizard...")
        onboard_action.triggered.connect(self._show_onboarding)
        quit_action = file_menu.addAction("Quit")
        quit_action.triggered.connect(self.close)

        help_menu = menu_bar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self._show_about)

        self._status_widget = QStatusBar()
        self.setStatusBar(self._status_widget)
        self._status_widget.showMessage("Ready")

    def _load_token(self) -> None:
        logger.info("Loading token from config")
        cfg = _load_config()
        if cfg.get("token"):
            logger.info("Token found in config file (length=%d)", len(cfg["token"]))
            self._token_input.setText(cfg["token"])
        else:
            logger.info("No token in config, trying keyring")
            try:
                import keyring

                token = keyring.get_password("disco-text", "bot-token")
                if token:
                    logger.info("Token found in keyring")
                    self._token_input.setText(token)
            except Exception as e:
                logger.warning("Keyring access failed: %s", e)
        logger.info("Token load complete")

    def _save_token(self, token: str) -> None:
        cfg = _load_config()
        cfg["token"] = token
        _save_config(cfg)
        try:
            import keyring

            keyring.set_password("disco-text", "bot-token", token)
        except Exception:
            pass

    def _connect(self) -> None:
        token = self._token_input.text().strip()
        if not token:
            QMessageBox.warning(self, "No Token", "Please enter a bot token.")
            return

        logger.info("Connecting with token (length=%d)", len(token))
        self._connect_btn.setEnabled(False)
        self._disconnect_btn.setEnabled(False)
        self._status_indicator.setText("● Connecting...")
        self._status_widget.showMessage("Connecting to Discord...")

        signals = _Signals(self._bridge)
        self._client.set_signals(signals)

        self._connect_worker = _ConnectWorker(self._client, token)
        self._connect_worker.start()

    def _disconnect(self) -> None:
        logger.info("Disconnecting")
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self._client.disconnect())
        except Exception:
            pass
        finally:
            loop.close()
        self._on_disconnected()

    def _on_connected(self) -> None:
        logger.info("_on_connected called")
        self._connect_btn.setEnabled(False)
        self._disconnect_btn.setEnabled(True)
        self._status_indicator.setText("● Connected")
        self._status_widget.showMessage("Connected to Discord")

        self._save_token(self._token_input.text().strip())

        guilds = self._client.get_guilds()
        logger.info("Populating server list with %d guilds", len(guilds))
        self._server_panel.populate(guilds)

    def _on_disconnected(self) -> None:
        logger.info("_on_disconnected called")
        self._connect_btn.setEnabled(True)
        self._disconnect_btn.setEnabled(False)
        self._status_indicator.setText("● Disconnected")
        self._status_widget.showMessage("Disconnected")
        self._server_panel.clear()
        self._channel_panel.clear()
        self._message_panel.clear()
        self._export_btn.setEnabled(False)
        self._export_selected_btn.setEnabled(False)

    def _on_error(self, message: str) -> None:
        logger.error("_on_error: %s", message)
        self._connect_btn.setEnabled(True)
        self._status_indicator.setText("● Error")
        self._status_widget.showMessage(f"Error: {message}")
        QMessageBox.critical(self, "Connection Error", message)

    def _on_server_selected(self, guild_id: str) -> None:
        logger.info("Server selected: guild_id=%s", guild_id)
        self._current_guild_id = guild_id
        self._channel_panel.show_loading()
        self._message_panel.clear()
        channels = self._client.get_text_channels(int(guild_id))
        logger.info("Populating channels: %d found", len(channels))
        self._channel_panel.populate(channels)

    def _on_channel_selected(self, channel_id: str) -> None:
        logger.info("Channel selected: channel_id=%s", channel_id)
        self._current_channel_id = channel_id
        self._message_panel.show_loading()
        self._status_widget.showMessage("Loading messages...")

        self._fetch_worker = _FetchWorker(self._client, int(channel_id))
        self._fetch_worker.finished.connect(self._on_messages_loaded)
        self._fetch_worker.error.connect(self._on_fetch_error)
        self._fetch_worker.progress.connect(self._on_fetch_progress)
        self._fetch_worker.start()

    def _on_fetch_progress(self, count: int) -> None:
        self._status_widget.showMessage(f"Loading messages... {count} fetched")
        self._message_panel.show_loading(count)

    def _on_messages_loaded(self, messages: list) -> None:
        logger.info("Loaded %d messages", len(messages))
        self._current_messages = messages
        channel_name = ""
        if self._current_channel_id and self._client.is_connected:
            ch = self._client.get_channel_by_id(int(self._current_channel_id))
            if ch:
                channel_name = ch.name
        self._message_panel.show_messages(messages, channel_name)
        self._export_btn.setEnabled(len(messages) > 0)
        self._export_selected_btn.setEnabled(False)
        self._status_widget.showMessage(f"Loaded {len(messages)} messages")

    def _on_fetch_error(self, message: str) -> None:
        logger.error("Fetch error: %s", message)
        self._status_widget.showMessage(f"Error: {message}")
        self._message_panel.clear()
        self._export_btn.setEnabled(False)
        self._export_selected_btn.setEnabled(False)

    def _on_message_selection_changed(self) -> None:
        selected = self._message_panel.get_selected_messages()
        total = len(self._current_messages)
        if len(selected) == total or len(selected) == 0:
            self._export_selected_btn.setEnabled(False)
            self._status_widget.showMessage(f"Loaded {total} messages")
        else:
            self._export_selected_btn.setEnabled(True)
            sel_range = self._message_panel.get_selection_range()
            if sel_range:
                self._status_widget.showMessage(
                    f"Selected messages {sel_range[0] + 1}\u2013{sel_range[1] + 1} of {total}"
                )

    def _show_export_dialog(self) -> None:
        if not self._current_messages:
            return
        self._do_export(self._current_messages)

    def _show_export_selected_dialog(self) -> None:
        selected = self._message_panel.get_selected_messages()
        if not selected or len(selected) == len(self._current_messages):
            return
        self._do_export(selected)

    def _do_export(self, messages: list) -> None:
        channel_name = ""
        server_name = ""
        if self._current_channel_id and self._client.is_connected:
            ch = self._client.get_channel_by_id(int(self._current_channel_id))
            if ch:
                channel_name = ch.name
                if ch.guild:
                    server_name = ch.guild.name
        dlg = ExportDialog(
            messages, channel_name, server_name, len(self._current_messages), self
        )
        dlg.exec()

    def _show_onboarding(self) -> None:
        logger.info("Opening onboarding wizard")
        wizard = OnboardingWizard(self)
        result = wizard.exec()
        logger.info("Onboarding wizard finished with result: %s", result)
        if result:
            token = wizard.get_token()
            if token:
                logger.info("Token received from wizard (length=%d)", len(token))
                self._token_input.setText(token)
        cfg = _load_config()
        cfg["onboarded"] = True
        _save_config(cfg)
        logger.info("Onboarding marked complete")

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "About Disco-Text",
            "Disco-Text v0.1.0\n\n"
            "Export Discord channel messages to text files "
            "for easy AI consumption.",
        )
