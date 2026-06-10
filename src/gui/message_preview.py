import discord
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

MAX_MESSAGE_LENGTH = 300

MATCH_BG = QColor(113, 63, 237, 60)
MATCH_CURRENT_BG = QColor(113, 63, 237, 120)
SELECTION_START_BG = QColor(72, 187, 120, 80)
SELECTION_RANGE_BG = QColor(72, 187, 120, 40)


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

        search_bar = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search messages...")
        self._search_input.setClearButtonEnabled(True)
        self._search_input.textChanged.connect(self._on_search_text_changed)
        search_bar.addWidget(self._search_input, 1)

        self._prev_btn = QPushButton("\u25b2")
        self._prev_btn.setObjectName("nav")
        self._prev_btn.setFixedWidth(30)
        self._prev_btn.setToolTip("Previous match")
        self._prev_btn.clicked.connect(self._go_prev_match)
        self._prev_btn.setEnabled(False)
        search_bar.addWidget(self._prev_btn)

        self._next_btn = QPushButton("\u25bc")
        self._next_btn.setObjectName("nav")
        self._next_btn.setFixedWidth(30)
        self._next_btn.setToolTip("Next match")
        self._next_btn.clicked.connect(self._go_next_match)
        self._next_btn.setEnabled(False)
        search_bar.addWidget(self._next_btn)

        layout.addLayout(search_bar)

        self._match_label = QLabel("")
        self._match_label.setObjectName("subheading")
        layout.addWidget(self._match_label)

        self._list = QListWidget()
        self._list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self._list.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self._list, 1)

        sel_bar = QHBoxLayout()

        self._set_start_btn = QPushButton("Set Start")
        self._set_start_btn.setObjectName("secondary")
        self._set_start_btn.setToolTip("Mark current message as export range start")
        self._set_start_btn.clicked.connect(self._set_range_start)
        sel_bar.addWidget(self._set_start_btn)

        self._set_end_btn = QPushButton("Set End")
        self._set_end_btn.setObjectName("secondary")
        self._set_end_btn.setToolTip("Mark current message as export range end")
        self._set_end_btn.clicked.connect(self._set_range_end)
        sel_bar.addWidget(self._set_end_btn)

        self._clear_sel_btn = QPushButton("Clear Sel")
        self._clear_sel_btn.setObjectName("secondary")
        self._clear_sel_btn.setToolTip("Clear the export range selection")
        self._clear_sel_btn.clicked.connect(self._clear_selection)
        sel_bar.addWidget(self._clear_sel_btn)

        sel_bar.addStretch()

        self._sel_label = QLabel("No selection")
        self._sel_label.setObjectName("subheading")
        sel_bar.addWidget(self._sel_label)

        layout.addLayout(sel_bar)

        self._messages: list[discord.Message] = []
        self._search_query: str = ""
        self._match_indices: list[int] = []
        self._current_match: int = -1
        self._range_start: int | None = None
        self._range_end: int | None = None
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self._do_search)

    def show_messages(self, messages: list[discord.Message], channel_name: str = "") -> None:
        self._messages = messages
        self._range_start = None
        self._range_end = None
        self._search_query = ""
        self._match_indices = []
        self._current_match = -1
        self._search_input.clear()
        self._match_label.setText("")
        self._update_sel_label()

        label = "Messages"
        if channel_name:
            label = f"Messages \u2014 {channel_name}"
        label += f" ({len(messages)})"
        self._heading.setText(label)

        self._list.clear()
        for msg in messages:
            display = self._format_message(msg)
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
        else:
            self._heading.setText("Messages \u2014 Loading...")
        self._list.clear()
        text = f"Loading messages... {count} fetched so far" if count else "Loading messages..."
        item = QListWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        font = item.font()
        font.setItalic(True)
        item.setFont(font)
        self._list.addItem(item)

    def get_selected_messages(self) -> list[discord.Message]:
        if self._range_start is not None and self._range_end is not None:
            start = min(self._range_start, self._range_end)
            end = max(self._range_start, self._range_end)
            return self._messages[start:end + 1]

        indices = set()
        for item in self._list.selectedItems():
            idx = item.data(Qt.ItemDataRole.UserRole)
            if idx is not None:
                indices.add(idx)
        if not indices:
            return self._messages
        return [self._messages[i] for i in sorted(indices) if 0 <= i < len(self._messages)]

    def get_selection_range(self) -> tuple[int, int] | None:
        if self._range_start is not None and self._range_end is not None:
            return (
                min(self._range_start, self._range_end),
                max(self._range_start, self._range_end),
            )
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

    @staticmethod
    def _format_message(msg: discord.Message) -> str:
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
        return display

    def _on_search_text_changed(self, text: str) -> None:
        self._search_query = text.strip().lower()
        self._search_timer.start()

    def _do_search(self) -> None:
        self._match_indices = []
        self._current_match = -1
        self._apply_highlights()

        if not self._search_query:
            self._match_label.setText("")
            self._prev_btn.setEnabled(False)
            self._next_btn.setEnabled(False)
            return

        for i, msg in enumerate(self._messages):
            search_text = self._format_message(msg).lower()
            if self._search_query in search_text:
                self._match_indices.append(i)

        if self._match_indices:
            self._current_match = 0
            self._apply_highlights()
            self._scroll_to_match(0)
            self._prev_btn.setEnabled(True)
            self._next_btn.setEnabled(True)
            self._update_match_label()
        else:
            self._match_label.setText("No matches")
            self._prev_btn.setEnabled(False)
            self._next_btn.setEnabled(False)

    def _apply_highlights(self) -> None:
        for i in range(self._list.count()):
            item = self._list.item(i)
            idx = item.data(Qt.ItemDataRole.UserRole)
            if idx is None:
                continue

            item.setBackground(QColor(0, 0, 0, 0))

            if idx in self._match_indices:
                match_pos = self._match_indices.index(idx) if idx in self._match_indices else -1
                if match_pos == self._current_match:
                    item.setBackground(MATCH_CURRENT_BG)
                else:
                    item.setBackground(MATCH_BG)

            if self._range_start is not None and self._range_end is not None:
                sel_min = min(self._range_start, self._range_end)
                sel_max = max(self._range_start, self._range_end)
                if sel_min <= idx <= sel_max:
                    item.setBackground(SELECTION_RANGE_BG)
                if idx == self._range_start or idx == self._range_end:
                    item.setBackground(SELECTION_START_BG)

    def _scroll_to_match(self, match_index: int) -> None:
        if not self._match_indices or match_index < 0 or match_index >= len(self._match_indices):
            return
        msg_idx = self._match_indices[match_index]
        list_row = self._find_list_row_for_index(msg_idx)
        if list_row is not None:
            self._list.setCurrentRow(list_row)
            self._list.scrollToItem(self._list.item(list_row))

    def _find_list_row_for_index(self, msg_index: int) -> int | None:
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == msg_index:
                return i
        return None

    def _go_prev_match(self) -> None:
        if not self._match_indices:
            return
        self._current_match = (self._current_match - 1) % len(self._match_indices)
        self._apply_highlights()
        self._scroll_to_match(self._current_match)
        self._update_match_label()

    def _go_next_match(self) -> None:
        if not self._match_indices:
            return
        self._current_match = (self._current_match + 1) % len(self._match_indices)
        self._apply_highlights()
        self._scroll_to_match(self._current_match)
        self._update_match_label()

    def _update_match_label(self) -> None:
        if not self._match_indices:
            self._match_label.setText("No matches" if self._search_query else "")
        else:
            self._match_label.setText(
                f"Match {self._current_match + 1} of {len(self._match_indices)}"
            )

    def _set_range_start(self) -> None:
        current = self._list.currentRow()
        if current < 0:
            return
        idx = self._list.item(current).data(Qt.ItemDataRole.UserRole)
        if idx is None:
            return
        self._range_start = idx
        if self._range_end is None:
            self._range_end = idx
        self._apply_highlights()
        self._update_sel_label()
        self.selection_changed.emit()

    def _set_range_end(self) -> None:
        current = self._list.currentRow()
        if current < 0:
            return
        idx = self._list.item(current).data(Qt.ItemDataRole.UserRole)
        if idx is None:
            return
        self._range_end = idx
        if self._range_start is None:
            self._range_start = idx
        self._apply_highlights()
        self._update_sel_label()
        self.selection_changed.emit()

    def _clear_selection(self) -> None:
        self._range_start = None
        self._range_end = None
        self._list.clearSelection()
        self._apply_highlights()
        self._update_sel_label()
        self.selection_changed.emit()

    def _update_sel_label(self) -> None:
        if self._range_start is not None and self._range_end is not None:
            start = min(self._range_start, self._range_end)
            end = max(self._range_start, self._range_end)
            self._sel_label.setText(f"Selected {start + 1}\u2013{end + 1} of {len(self._messages)}")
        elif self._list.selectedItems():
            indices = []
            for item in self._list.selectedItems():
                idx = item.data(Qt.ItemDataRole.UserRole)
                if idx is not None:
                    indices.append(idx)
            if indices:
                self._sel_label.setText(f"Selected {len(indices)} messages")
            else:
                self._sel_label.setText("No selection")
        else:
            self._sel_label.setText("No selection \u2014 click Set Start to begin")

    def _on_selection_changed(self) -> None:
        self._update_sel_label()
        self.selection_changed.emit()

    def clear(self) -> None:
        self._messages = []
        self._range_start = None
        self._range_end = None
        self._match_indices = []
        self._current_match = -1
        self._search_query = ""
        self._heading.setText("Messages")
        self._list.clear()
        self._match_label.setText("")
        self._sel_label.setText("No selection \u2014 click Set Start to begin")
        self._prev_btn.setEnabled(False)
        self._next_btn.setEnabled(False)
