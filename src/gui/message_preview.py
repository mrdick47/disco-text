import enum

import discord
from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPixmap, QPolygonF
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

MAX_MESSAGE_LENGTH = 300

RANGE_BG = "#7c3aed"

_ICON_SIZE = 16
_ACCENT = QColor("#7c3aed")


def _make_from_icon() -> QIcon:
    px = QPixmap(_ICON_SIZE, _ICON_SIZE)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QBrush(_ACCENT))
    p.setPen(Qt.PenStyle.NoPen)
    tri = QPolygonF()
    tri.append(QPointF(3, 2))
    tri.append(QPointF(3, 14))
    tri.append(QPointF(14, 8))
    p.drawPolygon(tri)
    p.end()
    return QIcon(px)


def _make_to_icon() -> QIcon:
    px = QPixmap(_ICON_SIZE, _ICON_SIZE)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QBrush(_ACCENT))
    p.setPen(Qt.PenStyle.NoPen)
    tri = QPolygonF()
    tri.append(QPointF(13, 2))
    tri.append(QPointF(13, 14))
    tri.append(QPointF(2, 8))
    p.drawPolygon(tri)
    p.end()
    return QIcon(px)


def _make_bar_icon() -> QIcon:
    px = QPixmap(_ICON_SIZE, _ICON_SIZE)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QBrush(_ACCENT))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRect(QRectF(6, 0, 4, _ICON_SIZE))
    p.end()
    return QIcon(px)


class SelectionMode(enum.Enum):
    RANGE = "range"
    CHECKBOX = "checkbox"


class MessagePreviewPanel(QWidget):
    selection_changed = pyqtSignal()
    mode_changed = pyqtSignal(str)

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
        self._list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._show_context_menu)
        self._list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self._list.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self._list, 1)

        self._toolbar = QHBoxLayout()

        self._set_from_btn = QPushButton("Set From")
        self._set_from_btn.setObjectName("secondary")
        self._set_from_btn.setToolTip("Set current message as range start")
        self._set_from_btn.clicked.connect(self._set_range_from)
        self._toolbar.addWidget(self._set_from_btn)

        self._set_to_btn = QPushButton("Set To")
        self._set_to_btn.setObjectName("secondary")
        self._set_to_btn.setToolTip("Set current message as range end")
        self._set_to_btn.clicked.connect(self._set_range_to)
        self._toolbar.addWidget(self._set_to_btn)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setObjectName("secondary")
        self._clear_btn.setToolTip("Clear the range selection")
        self._clear_btn.clicked.connect(self._clear_range)
        self._toolbar.addWidget(self._clear_btn)

        self._select_all_btn = QPushButton("Select All")
        self._select_all_btn.setObjectName("secondary")
        self._select_all_btn.setToolTip("Check all messages")
        self._select_all_btn.clicked.connect(self._select_all)
        self._select_all_btn.setVisible(False)
        self._toolbar.addWidget(self._select_all_btn)

        self._clear_all_btn = QPushButton("Clear All")
        self._clear_all_btn.setObjectName("secondary")
        self._clear_all_btn.setToolTip("Uncheck all messages")
        self._clear_all_btn.clicked.connect(self._clear_all)
        self._clear_all_btn.setVisible(False)
        self._toolbar.addWidget(self._clear_all_btn)

        self._toolbar.addStretch()

        self._sel_label = QLabel("Range \u2014 No selection")
        self._sel_label.setObjectName("subheading")
        self._toolbar.addWidget(self._sel_label)

        layout.addLayout(self._toolbar)

        self._messages: list[discord.Message] = []
        self._search_query: str = ""
        self._match_indices: list[int] = []
        self._current_match: int = -1
        self._base_font: QFont | None = None
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self._do_search)

        self._mode = SelectionMode.RANGE
        self._range_from: int | None = None
        self._range_to: int | None = None
        self._block_item_changed = False
        self._context_item: QListWidgetItem | None = None
        self._from_icon = _make_from_icon()
        self._to_icon = _make_to_icon()
        self._bar_icon = _make_bar_icon()

    def set_mode(self, mode: SelectionMode) -> None:
        self._mode = mode
        self._range_from = None
        self._range_to = None

        range_visible = mode == SelectionMode.RANGE
        self._set_from_btn.setVisible(range_visible)
        self._set_to_btn.setVisible(range_visible)
        self._clear_btn.setVisible(range_visible)
        self._select_all_btn.setVisible(not range_visible)
        self._clear_all_btn.setVisible(not range_visible)

        if mode == SelectionMode.RANGE:
            self._list.setSelectionMode(
                QListWidget.SelectionMode.SingleSelection
            )
        else:
            self._list.clearSelection()
            self._list.setSelectionMode(
                QListWidget.SelectionMode.ExtendedSelection
            )

        self._block_item_changed = True
        for i in range(self._list.count()):
            item = self._list.item(i)
            idx = item.data(Qt.ItemDataRole.UserRole)
            if idx is None:
                continue
            if mode == SelectionMode.CHECKBOX:
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
            else:
                flags = item.flags()
                flags &= ~Qt.ItemFlag.ItemIsUserCheckable
                item.setFlags(flags)
                item.setData(Qt.ItemDataRole.CheckStateRole, None)
        self._block_item_changed = False

        self._refresh_all_items()
        self._update_sel_label()
        self.mode_changed.emit(mode.value)

    def show_messages(
        self, messages: list[discord.Message], channel_name: str = ""
    ) -> None:
        self._messages = messages
        self._range_from = None
        self._range_to = None
        self._search_query = ""
        self._match_indices = []
        self._current_match = -1
        self._search_input.clear()
        self._match_label.setText("")

        label = "Messages"
        if channel_name:
            label = f"Messages \u2014 {channel_name}"
        label += f" ({len(messages)})"
        self._heading.setText(label)

        self._block_item_changed = True
        self._list.clear()
        for i, msg in enumerate(messages):
            display = self._format_message(msg)
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, i)
            font = item.font()
            font.setPointSize(10)
            item.setFont(font)
            if self._mode == SelectionMode.CHECKBOX:
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
            self._list.addItem(item)
        self._block_item_changed = False

        if self._list.count() > 0:
            self._base_font = QFont(self._list.item(0).font())

        self._update_sel_label()

    def show_loading(self, count: int = 0) -> None:
        if count > 0:
            self._heading.setText(
                f"Messages \u2014 Loading... ({count} fetched)"
            )
        else:
            self._heading.setText("Messages \u2014 Loading...")
        self._list.clear()
        text = (
            f"Loading messages... {count} fetched so far"
            if count
            else "Loading messages..."
        )
        item = QListWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        font = item.font()
        font.setItalic(True)
        item.setFont(font)
        self._list.addItem(item)

    def get_selected_messages(self) -> list[discord.Message]:
        if self._mode == SelectionMode.RANGE:
            if self._range_from is not None and self._range_to is not None:
                lo = min(self._range_from, self._range_to)
                hi = max(self._range_from, self._range_to)
                return self._messages[lo : hi + 1]
            return self._messages
        else:
            indices: list[int] = []
            for i in range(self._list.count()):
                item = self._list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    idx = item.data(Qt.ItemDataRole.UserRole)
                    if idx is not None:
                        indices.append(idx)
            if not indices:
                return self._messages
            return [
                self._messages[i]
                for i in sorted(indices)
                if 0 <= i < len(self._messages)
            ]

    def get_selection_range(self) -> tuple[int, int] | None:
        if self._mode == SelectionMode.RANGE:
            if self._range_from is not None and self._range_to is not None:
                return (
                    min(self._range_from, self._range_to),
                    max(self._range_from, self._range_to),
                )
            return None
        else:
            indices: list[int] = []
            for i in range(self._list.count()):
                item = self._list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    idx = item.data(Qt.ItemDataRole.UserRole)
                    if idx is not None:
                        indices.append(idx)
            if indices:
                return (min(indices), max(indices))
            return None

    @staticmethod
    def _format_message(msg: discord.Message) -> str:
        timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        author = msg.author.display_name
        content = msg.content or "(no text content)"
        if len(content) > MAX_MESSAGE_LENGTH:
            content = content[:MAX_MESSAGE_LENGTH] + "..."
        parts: list[str] = []
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

        if not self._search_query:
            self._refresh_all_items()
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
            self._refresh_all_items()
            self._scroll_to_match(0)
            self._prev_btn.setEnabled(True)
            self._next_btn.setEnabled(True)
            self._update_match_label()
        else:
            self._refresh_all_items()
            self._match_label.setText("No matches")
            self._prev_btn.setEnabled(False)
            self._next_btn.setEnabled(False)

    def _refresh_all_items(self) -> None:
        range_min: int | None = None
        range_max: int | None = None
        if self._range_from is not None and self._range_to is not None:
            range_min = min(self._range_from, self._range_to)
            range_max = max(self._range_from, self._range_to)

        self._block_item_changed = True
        for i in range(self._list.count()):
            item = self._list.item(i)
            idx = item.data(Qt.ItemDataRole.UserRole)
            if idx is None:
                continue

            font = QFont(self._base_font if self._base_font else item.font())
            font.setPointSize(10)
            font.setBold(False)

            if idx in self._match_indices:
                font.setBold(True)

            item.setFont(font)

            if self._mode == SelectionMode.RANGE:
                in_range = (
                    range_min is not None and range_min <= idx <= range_max
                )
                is_from = idx == self._range_from
                is_to = idx == self._range_to

                if in_range:
                    item.setBackground(QBrush(QColor(RANGE_BG)))
                else:
                    item.setBackground(QBrush())

                if is_from and is_to:
                    item.setIcon(self._from_icon)
                elif is_from:
                    item.setIcon(self._from_icon)
                elif is_to:
                    item.setIcon(self._to_icon)
                elif in_range:
                    item.setIcon(self._bar_icon)
                else:
                    item.setIcon(QIcon())
            else:
                item.setBackground(QBrush())
                item.setIcon(QIcon())

        self._block_item_changed = False

    def _scroll_to_match(self, match_index: int) -> None:
        if (
            not self._match_indices
            or match_index < 0
            or match_index >= len(self._match_indices)
        ):
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
        self._current_match = (self._current_match - 1) % len(
            self._match_indices
        )
        self._refresh_all_items()
        self._scroll_to_match(self._current_match)
        self._update_match_label()

    def _go_next_match(self) -> None:
        if not self._match_indices:
            return
        self._current_match = (self._current_match + 1) % len(
            self._match_indices
        )
        self._refresh_all_items()
        self._scroll_to_match(self._current_match)
        self._update_match_label()

    def _update_match_label(self) -> None:
        if not self._match_indices:
            self._match_label.setText(
                "No matches" if self._search_query else ""
            )
        else:
            self._match_label.setText(
                f"Match {self._current_match + 1} of {len(self._match_indices)}"
            )

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        if self._mode == SelectionMode.RANGE:
            idx = item.data(Qt.ItemDataRole.UserRole)
            if idx is None:
                return

            if self._range_from is None:
                self._range_from = idx
                self._range_to = None
            elif self._range_to is None:
                if idx < self._range_from:
                    self._range_to = self._range_from
                    self._range_from = idx
                else:
                    self._range_to = idx
            else:
                if idx < self._range_from:
                    self._range_from = idx
                elif idx > self._range_to:
                    self._range_to = idx
                else:
                    dist_from = idx - self._range_from
                    dist_to = self._range_to - idx
                    if dist_from <= dist_to:
                        self._range_from = idx
                    else:
                        self._range_to = idx

            self._refresh_all_items()
            self._update_sel_label()
            self.selection_changed.emit()
        elif self._mode == SelectionMode.CHECKBOX:
            idx = item.data(Qt.ItemDataRole.UserRole)
            if idx is None:
                return
            new_state = (
                Qt.CheckState.Unchecked
                if item.checkState() == Qt.CheckState.Checked
                else Qt.CheckState.Checked
            )
            self._block_item_changed = True
            item.setCheckState(new_state)
            self._block_item_changed = False
            self._update_sel_label()
            self.selection_changed.emit()

    def _show_context_menu(self, pos) -> None:
        menu = QMenu(self)
        if self._mode == SelectionMode.RANGE:
            item = self._list.itemAt(pos)
            if item:
                self._context_item = item
                menu.addAction("Set as From", self._set_range_from_context)
                menu.addAction("Set as To", self._set_range_to_context)
                menu.addSeparator()
            menu.addAction("Clear Selection", self._clear_range)
        else:
            menu.addAction("Check Selected", self._check_selected)
            menu.addAction("Uncheck Selected", self._uncheck_selected)
            menu.addSeparator()
            menu.addAction("Check All", self._select_all)
            menu.addAction("Uncheck All", self._clear_all)
        menu.exec(self._list.viewport().mapToGlobal(pos))

    def _set_range_from(self) -> None:
        row = self._list.currentRow()
        if row < 0:
            return
        item = self._list.item(row)
        idx = item.data(Qt.ItemDataRole.UserRole)
        if idx is None:
            return
        self._range_from = idx
        self._refresh_all_items()
        self._update_sel_label()
        self.selection_changed.emit()

    def _set_range_to(self) -> None:
        row = self._list.currentRow()
        if row < 0:
            return
        item = self._list.item(row)
        idx = item.data(Qt.ItemDataRole.UserRole)
        if idx is None:
            return
        self._range_to = idx
        if self._range_from is not None and self._range_to < self._range_from:
            self._range_to, self._range_from = self._range_from, self._range_to
        self._refresh_all_items()
        self._update_sel_label()
        self.selection_changed.emit()

    def _set_range_from_context(self) -> None:
        if self._context_item is None:
            return
        idx = self._context_item.data(Qt.ItemDataRole.UserRole)
        if idx is None:
            return
        self._range_from = idx
        if self._range_to is not None and self._range_from > self._range_to:
            self._range_from, self._range_to = self._range_to, self._range_from
        self._refresh_all_items()
        self._update_sel_label()
        self.selection_changed.emit()

    def _set_range_to_context(self) -> None:
        if self._context_item is None:
            return
        idx = self._context_item.data(Qt.ItemDataRole.UserRole)
        if idx is None:
            return
        self._range_to = idx
        if self._range_from is not None and self._range_to < self._range_from:
            self._range_from, self._range_to = self._range_to, self._range_from
        self._refresh_all_items()
        self._update_sel_label()
        self.selection_changed.emit()

    def _clear_range(self) -> None:
        self._range_from = None
        self._range_to = None
        self._refresh_all_items()
        self._update_sel_label()
        self.selection_changed.emit()

    def _select_all(self) -> None:
        self._block_item_changed = True
        for i in range(self._list.count()):
            item = self._list.item(i)
            idx = item.data(Qt.ItemDataRole.UserRole)
            if idx is not None:
                item.setCheckState(Qt.CheckState.Checked)
        self._block_item_changed = False
        self._update_sel_label()
        self.selection_changed.emit()

    def _clear_all(self) -> None:
        self._block_item_changed = True
        for i in range(self._list.count()):
            item = self._list.item(i)
            idx = item.data(Qt.ItemDataRole.UserRole)
            if idx is not None:
                item.setCheckState(Qt.CheckState.Unchecked)
        self._block_item_changed = False
        self._update_sel_label()
        self.selection_changed.emit()

    def _on_item_changed(self, item: QListWidgetItem) -> None:
        if self._block_item_changed:
            return
        if self._mode != SelectionMode.CHECKBOX:
            return
        self._update_sel_label()
        self.selection_changed.emit()

    def _check_selected(self) -> None:
        self._block_item_changed = True
        for item in self._list.selectedItems():
            item.setCheckState(Qt.CheckState.Checked)
        self._block_item_changed = False
        self._update_sel_label()
        self.selection_changed.emit()

    def _uncheck_selected(self) -> None:
        self._block_item_changed = True
        for item in self._list.selectedItems():
            item.setCheckState(Qt.CheckState.Unchecked)
        self._block_item_changed = False
        self._update_sel_label()
        self.selection_changed.emit()

    def _update_sel_label(self) -> None:
        total = len(self._messages)
        if self._mode == SelectionMode.RANGE:
            if self._range_from is not None and self._range_to is not None:
                lo = min(self._range_from, self._range_to)
                hi = max(self._range_from, self._range_to)
                self._sel_label.setText(
                    f"Range \u2014 {lo + 1}\u2013{hi + 1} of {total}"
                )
            else:
                self._sel_label.setText("Range \u2014 No selection")
        else:
            count = 0
            for i in range(self._list.count()):
                item = self._list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    idx = item.data(Qt.ItemDataRole.UserRole)
                    if idx is not None:
                        count += 1
            if count > 0:
                self._sel_label.setText(
                    f"Checkbox \u2014 {count} of {total} selected"
                )
            else:
                self._sel_label.setText("Checkbox \u2014 No selection")

    def clear(self) -> None:
        self._messages = []
        self._range_from = None
        self._range_to = None
        self._match_indices = []
        self._current_match = -1
        self._search_query = ""
        self._base_font = None
        self._heading.setText("Messages")
        self._list.clear()
        self._match_label.setText("")
        self._update_sel_label()
        self._prev_btn.setEnabled(False)
        self._next_btn.setEnabled(False)
