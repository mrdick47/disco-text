import discord
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ChannelListPanel(QWidget):
    channel_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._heading = QLabel("Channels")
        self._heading.setObjectName("heading")
        layout.addWidget(self._heading)

        self._list = QListWidget()
        self._list.currentItemChanged.connect(self._on_selection)
        layout.addWidget(self._list)

    def show_loading(self) -> None:
        self._heading.setText("Channels — Loading...")
        self._list.clear()
        item = QListWidgetItem("\u23f3 Loading channels...")
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        font = item.font()
        font.setItalic(True)
        item.setFont(font)
        self._list.addItem(item)

    def populate(self, channels: list[discord.TextChannel]) -> None:
        self._list.clear()
        self._heading.setText("Channels")
        current_category = None
        for channel in channels:
            cat_name = channel.category.name if channel.category else "Uncategorized"
            if cat_name != current_category:
                category_item = QListWidgetItem(f"\u2500\u2500 {cat_name} \u2500\u2500")
                category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                font = category_item.font()
                font.setBold(True)
                font.setPointSize(10)
                category_item.setFont(font)
                self._list.addItem(category_item)
                current_category = cat_name

            item = QListWidgetItem(f"# {channel.name}")
            item.setData(Qt.ItemDataRole.UserRole, str(channel.id))
            self._list.addItem(item)

        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) is not None:
                self._list.setCurrentRow(i)
                break

    def _on_selection(self, current: QListWidgetItem, _previous) -> None:
        if current is None:
            return
        channel_id_str = current.data(Qt.ItemDataRole.UserRole)
        if channel_id_str is not None:
            self.channel_selected.emit(channel_id_str)

    def clear(self) -> None:
        self._heading.setText("Channels")
        self._list.clear()
