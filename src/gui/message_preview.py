import discord
from PyQt6.QtWidgets import (
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class MessagePreviewPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._heading = QLabel("Messages")
        self._heading.setObjectName("heading")
        layout.addWidget(self._heading)

        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._text.setPlaceholderText("Select a channel to preview messages...")
        layout.addWidget(self._text)

    def show_messages(self, messages: list[discord.Message], channel_name: str = "") -> None:
        label = "Messages"
        if channel_name:
            label = f"Messages \u2014 {channel_name}"
        label += f" ({len(messages)})"
        self._heading.setText(label)
        lines = []
        for msg in messages:
            timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            author = msg.author.display_name
            content = msg.content or "(no text content)"
            parts = []
            for embed in msg.embeds:
                if embed.description:
                    parts.append(f"[Embed: {embed.description[:100]}]")
            for att in msg.attachments:
                parts.append(f"[Attachment: {att.filename}]")
            extra = " ".join(parts)
            lines.append(f"<b>{author}</b> <span style='color:#718096'>\u2014 {timestamp}</span>")
            lines.append(f"{content} {extra}")
            lines.append("")
        self._text.setHtml("<br>".join(lines))
        scrollbar = self._text.verticalScrollBar()
        scrollbar.setValue(scrollbar.minimum())

    def show_loading(self, count: int = 0) -> None:
        if count > 0:
            self._heading.setText(f"Messages \u2014 Loading... ({count} fetched)")
            self._text.setHtml(f"<i>Loading messages... {count} fetched so far</i>")
        else:
            self._heading.setText("Messages \u2014 Loading...")
            self._text.setHtml("<i>Loading messages...</i>")

    def clear(self) -> None:
        self._heading.setText("Messages")
        self._text.clear()
        self._text.setPlaceholderText("Select a channel to preview messages...")
