import discord
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from src.exporters.md_exporter import export_md
from src.exporters.txt_exporter import export_txt


class ExportDialog(QDialog):
    def __init__(
        self,
        messages: list[discord.Message],
        channel_name: str,
        server_name: str,
        total_count: int,
        parent=None,
    ):
        super().__init__(parent)
        self._messages = messages
        self._channel_name = channel_name
        self._server_name = server_name
        self._total_count = total_count

        self.setWindowTitle("Export Messages")
        self.setMinimumWidth(450)
        self.setup_ui()

    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        if len(self._messages) == self._total_count:
            info = QLabel(
                f"Exporting all {len(self._messages)} messages from #{self._channel_name}"
            )
        else:
            info = QLabel(
                f"Exporting {len(self._messages)} of {self._total_count} messages "
                f"from #{self._channel_name}"
            )
        info.setObjectName("subheading")
        layout.addWidget(info)

        format_group = QGroupBox("Format")
        format_layout = QVBoxLayout(format_group)
        self._txt_check = QCheckBox("Plain text (.txt)")
        self._txt_check.setChecked(True)
        self._md_check = QCheckBox("Markdown (.md)")
        self._md_check.setChecked(True)
        format_layout.addWidget(self._txt_check)
        format_layout.addWidget(self._md_check)
        layout.addWidget(format_group)

        btn_layout = QVBoxLayout()
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self._do_export)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _do_export(self) -> None:
        if not self._txt_check.isChecked() and not self._md_check.isChecked():
            QMessageBox.warning(self, "No Format", "Please select at least one export format.")
            return

        if not self._messages:
            QMessageBox.warning(self, "No Messages", "No messages to export.")
            return

        save_dir = QFileDialog.getExistingDirectory(self, "Choose Export Directory")
        if not save_dir:
            return

        safe_name = self._channel_name.replace(" ", "_")
        server_safe = self._server_name.replace(" ", "_")

        if len(self._messages) < self._total_count:
            first = self._messages[0].created_at.strftime("%Y%m%d")
            last = self._messages[-1].created_at.strftime("%Y%m%d")
            suffix = f"_{first}-{last}"
        else:
            suffix = ""

        if self._txt_check.isChecked():
            content = export_txt(self._messages, self._channel_name, self._server_name)
            path = f"{save_dir}/{server_safe}_{safe_name}{suffix}.txt"
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

        if self._md_check.isChecked():
            content = export_md(self._messages, self._channel_name, self._server_name)
            path = f"{save_dir}/{server_safe}_{safe_name}{suffix}.md"
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

        QMessageBox.information(self, "Export Complete", f"Messages exported to {save_dir}")
        self.accept()
