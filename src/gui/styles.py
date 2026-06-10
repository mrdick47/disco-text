DARK_BG = "#1e1e2e"
DARK_SURFACE = "#282840"
DARK_BORDER = "#3e3e5e"
ACCENT = "#7c3aed"
ACCENT_HOVER = "#6d28d9"
TEXT_PRIMARY = "#e2e8f0"
TEXT_SECONDARY = "#a0aec0"
TEXT_DIM = "#718096"
SUCCESS = "#48bb78"
ERROR = "#fc8181"

STYLESHEET = f"""
QMainWindow {{
    background-color: {DARK_BG};
}}
QWidget {{
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    font-size: 13px;
    background-color: {DARK_BG};
}}
QListWidget, QTreeWidget, QTableWidget {{
    background-color: {DARK_SURFACE};
    border: 1px solid {DARK_BORDER};
    border-radius: 6px;
    padding: 4px;
    outline: none;
}}
QListWidget::item, QTreeWidget::item {{
    padding: 6px 8px;
    border-radius: 4px;
}}
QListWidget::item:selected, QTreeWidget::item:selected {{
    background-color: {ACCENT};
    color: white;
}}
QListWidget::item:hover, QTreeWidget::item:hover {{
    background-color: {DARK_BORDER};
}}
QPushButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {ACCENT_HOVER};
}}
QPushButton:disabled {{
    background-color: {DARK_BORDER};
    color: {TEXT_DIM};
}}
QPushButton#secondary {{
    background-color: {DARK_SURFACE};
    border: 1px solid {DARK_BORDER};
}}
QPushButton#secondary:hover {{
    background-color: {DARK_BORDER};
}}
QLineEdit {{
    background-color: {DARK_SURFACE};
    border: 1px solid {DARK_BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    color: {TEXT_PRIMARY};
}}
QLineEdit:focus {{
    border-color: {ACCENT};
}}
QTextEdit {{
    background-color: {DARK_SURFACE};
    border: 1px solid {DARK_BORDER};
    border-radius: 6px;
    padding: 8px;
    color: {TEXT_PRIMARY};
}}
QLabel#heading {{
    font-size: 16px;
    font-weight: 700;
}}
QLabel#subheading {{
    font-size: 14px;
    color: {TEXT_SECONDARY};
}}
QCheckBox {{
    spacing: 6px;
    color: {TEXT_PRIMARY};
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid {DARK_BORDER};
    background-color: {DARK_SURFACE};
}}
QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border-color: {ACCENT};
}}
QDateEdit {{
    background-color: {DARK_SURFACE};
    border: 1px solid {DARK_BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    color: {TEXT_PRIMARY};
}}
QProgressBar {{
    background-color: {DARK_SURFACE};
    border: 1px solid {DARK_BORDER};
    border-radius: 6px;
    text-align: center;
    color: {TEXT_PRIMARY};
    height: 24px;
}}
QProgressBar::chunk {{
    background-color: {ACCENT};
    border-radius: 5px;
}}
QSplitter::handle {{
    background-color: {DARK_BORDER};
    width: 2px;
}}
QScrollArea {{
    border: none;
}}
QStatusBar {{
    background-color: {DARK_SURFACE};
    border-top: 1px solid {DARK_BORDER};
    color: {TEXT_SECONDARY};
}}
QMenuBar {{
    background-color: {DARK_SURFACE};
    border-bottom: 1px solid {DARK_BORDER};
}}
QMenuBar::item:selected {{
    background-color: {ACCENT};
}}
QMenu {{
    background-color: {DARK_SURFACE};
    border: 1px solid {DARK_BORDER};
}}
QMenu::item:selected {{
    background-color: {ACCENT};
}}
QGroupBox {{
    border: 1px solid {DARK_BORDER};
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: {TEXT_SECONDARY};
}}
QWizard {{
    background-color: {DARK_BG};
}}
QWizardPage {{
    background-color: {DARK_BG};
    color: {TEXT_PRIMARY};
}}
QWizard QLabel {{
    color: {TEXT_PRIMARY};
    background-color: transparent;
}}
QWizard QLineEdit {{
    background-color: {DARK_SURFACE};
    border: 1px solid {DARK_BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    color: {TEXT_PRIMARY};
}}
QWizard QPushButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    min-width: 80px;
}}
QWizard QPushButton:hover {{
    background-color: {ACCENT_HOVER};
}}
QWizard QPushButton:disabled {{
    background-color: {DARK_BORDER};
    color: {TEXT_DIM};
}}
QWizard QCommandLinkButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
}}
QFrame#wizardTitle {{ background-color: {DARK_BG}; }}
"""
