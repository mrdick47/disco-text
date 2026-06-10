import discord
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ServerListPanel(QWidget):
    server_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        heading = QLabel("Servers")
        heading.setObjectName("heading")
        layout.addWidget(heading)

        self._list = QListWidget()
        self._list.currentItemChanged.connect(self._on_selection)
        layout.addWidget(self._list)

    def populate(self, guilds: list[discord.Guild]) -> None:
        self._list.clear()
        for guild in guilds:
            item = QListWidgetItem(guild.name)
            item.setData(Qt.ItemDataRole.UserRole, str(guild.id))
            self._list.addItem(item)
        if self._list.count() > 0:
            self._list.setCurrentRow(0)

    def _on_selection(self, current: QListWidgetItem, _previous) -> None:
        if current is None:
            return
        guild_id_str = current.data(Qt.ItemDataRole.UserRole)
        self.server_selected.emit(guild_id_str)

    def clear(self) -> None:
        self._list.clear()
