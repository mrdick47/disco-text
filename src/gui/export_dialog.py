import discord
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QCheckBox,
    QDateEdit,
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
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
        parent=None,
    ):
        super().__init__(parent)
        self._messages = messages
        self._channel_name = channel_name
        self._server_name = server_name

        self.setWindowTitle("Export Messages")
        self.setMinimumWidth(450)
        self.setup_ui()

    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        info = QLabel(f"Exporting {len(self._messages)} messages from #{self._channel_name}")
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

        date_group = QGroupBox("Date Range")
        date_layout = QVBoxLayout(date_group)
        self._all_radio = QCheckBox("Export all messages")
        self._all_radio.setChecked(True)
        self._all_radio.toggled.connect(self._toggle_date_pickers)
        date_layout.addWidget(self._all_radio)

        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("From:"))
        self._from_date = QDateEdit()
        self._from_date.setCalendarPopup(True)
        self._from_date.setDate(QDate.currentDate().addMonths(-1))
        self._from_date.setEnabled(False)
        range_layout.addWidget(self._from_date)

        range_layout.addWidget(QLabel("To:"))
        self._to_date = QDateEdit()
        self._to_date.setCalendarPopup(True)
        self._to_date.setDate(QDate.currentDate())
        self._to_date.setEnabled(False)
        range_layout.addWidget(self._to_date)
        date_layout.addLayout(range_layout)
        layout.addWidget(date_group)

        btn_layout = QHBoxLayout()
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self._do_export)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _toggle_date_pickers(self, checked: bool) -> None:
        self._from_date.setEnabled(not checked)
        self._to_date.setEnabled(not checked)

    def _do_export(self) -> None:
        if not self._txt_check.isChecked() and not self._md_check.isChecked():
            QMessageBox.warning(self, "No Format", "Please select at least one export format.")
            return

        export_all = self._all_radio.isChecked()
        messages = self._messages
        if not export_all:
            from_dt = self._from_date.dateTime().toPyDateTime()
            to_dt = self._to_date.dateTime().toPyDateTime()
            messages = [m for m in self._messages if from_dt <= m.created_at <= to_dt]

        if not messages:
            QMessageBox.warning(
                self, "No Messages", "No messages found in the selected date range."
            )
            return

        save_dir = QFileDialog.getExistingDirectory(self, "Choose Export Directory")
        if not save_dir:
            return

        safe_name = self._channel_name.replace(" ", "_")
        server_safe = self._server_name.replace(" ", "_")

        if self._txt_check.isChecked():
            content = export_txt(messages, self._channel_name, self._server_name)
            path = f"{save_dir}/{server_safe}_{safe_name}.txt"
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

        if self._md_check.isChecked():
            content = export_md(messages, self._channel_name, self._server_name)
            path = f"{save_dir}/{server_safe}_{safe_name}.md"
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

        QMessageBox.information(self, "Export Complete", f"Messages exported to {save_dir}")
        self.accept()
