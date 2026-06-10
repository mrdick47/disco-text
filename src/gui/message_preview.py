import discord
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

MAX_MESSAGE_LENGTH = 300


class MessagePreviewPanel(QWidget):
    selection_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._heading = QLabel("Messages")
        self._heading.setObjectName("heading")
        layout.addWidget(self._heading)

        self._list = QListWidget()
        self._list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self._list.currentItemChanged.connect(self._on_current_changed)
        self._list.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self._list)

        self._messages: list[discord.Message] = []

    def show_messages(self, messages: list[discord.Message], channel_name: str = "") -> None:
        self._messages = messages
        label = "Messages"
        if channel_name:
            label = f"Messages \u2014 {channel_name}"
        label += f" ({len(messages)})"
        self._heading.setText(label)

        self._list.clear()
        for msg in messages:
            timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            author = msg.author.display_name
            content = msg.content or "(no text content)"
            if len(content) > MAX_MESSAGE_LENGTH:
                content = content[:MAX_MESSAGE_LENGTH] + "..."
            parts = []
            for embed in msg.embeds:
                if embed.description:
                    parts.append("[Embed]")
            for att in msg.attachments:
                parts.append(f"[{att.filename}]")
            extra = " ".join(parts)
            display = f"{author} \u2014 {timestamp}: {content}"
            if extra:
                display += f" {extra}"

            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, messages.index(msg))
            font = item.font()
            font.setPointSize(10)
            item.setFont(font)
            self._list.addItem(item)

        if self._list.count() > 0:
            self._list.setCurrentRow(0)

    def show_loading(self, count: int = 0) -> None:
        if count > 0:
            self._heading.setText(f"Messages \u2014 Loading... ({count} fetched)")
            self._list.clear()
            item = QListWidgetItem(f"Loading messages... {count} fetched so far")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            font = item.font()
            font.setItalic(True)
            item.setFont(font)
            self._list.addItem(item)
        else:
            self._heading.setText("Messages \u2014 Loading...")
            self._list.clear()
            item = QListWidgetItem("Loading messages...")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            font = item.font()
            font.setItalic(True)
            item.setFont(font)
            self._list.addItem(item)

    def get_selected_messages(self) -> list[discord.Message]:
        indices = set()
        for item in self._list.selectedItems():
            idx = item.data(Qt.ItemDataRole.UserRole)
            if idx is not None:
                indices.add(idx)
        if not indices:
            return self._messages
        return [self._messages[i] for i in sorted(indices) if 0 <= i < len(self._messages)]

    def get_selection_range(self) -> tuple[int, int] | None:
        selected = self._list.selectedItems()
        if not selected:
            return None
        indices = []
        for item in selected:
            idx = item.data(Qt.ItemDataRole.UserRole)
            if idx is not None:
                indices.append(idx)
        if not indices:
            return None
        return (min(indices), max(indices))

    def _on_current_changed(self, current, _previous) -> None:
        pass

    def _on_selection_changed(self) -> None:
        self.selection_changed.emit()

    def clear(self) -> None:
        self._messages = []
        self._heading.setText("Messages")
        self._list.clear()
