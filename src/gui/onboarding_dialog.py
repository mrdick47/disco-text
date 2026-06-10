import logging

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWizard,
    QWizardPage,
)

logger = logging.getLogger(__name__)

DARK_BG = "#1e1e2e"
DARK_SURFACE = "#282840"
TEXT_PRIMARY = "#e2e8f0"


def _apply_dark_palette(widget):
    palette = widget.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor(DARK_BG))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Base, QColor(DARK_SURFACE))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Button, QColor(DARK_SURFACE))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT_PRIMARY))
    widget.setPalette(palette)
    widget.setAutoFillBackground(True)


def _label(text: str, word_wrap: bool = True) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(word_wrap)
    return label


class WelcomePage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Welcome to Disco-Text")
        layout = QVBoxLayout(self)

        layout.addWidget(_label(
            "Disco-Text lets you export Discord channel messages into text files "
            "that are easy to feed into AI tools.\n\n"
            "To get started, you need a Discord Bot Token. This wizard will walk "
            "you through creating one."
        ))

        layout.addWidget(QLabel(""))
        layout.addWidget(_label("You'll need:"))
        layout.addWidget(_label("  \u2022 A Discord account"))
        layout.addWidget(_label("  \u2022 Permission to add bots to your server"))
        layout.addWidget(_label("  \u2022 About 2 minutes"))


class CreateAppPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Step 1: Create a Discord Application")
        layout = QVBoxLayout(self)

        layout.addWidget(_label("1. Go to the Discord Developer Portal:"))
        link = QLabel(
            '<a href="https://discord.com/developers/applications">'
            'https://discord.com/developers/applications</a>'
        )
        link.setOpenExternalLinks(True)
        layout.addWidget(link)

        layout.addWidget(QLabel(""))
        layout.addWidget(_label("2. Click \"New Application\""))
        layout.addWidget(_label("3. Give it a name (e.g., \"Disco-Text Exporter\")"))
        layout.addWidget(_label("4. Click \"Create\""))


class CreateBotPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Step 2: Configure the Bot & Get Token")
        layout = QVBoxLayout(self)

        layout.addWidget(_label(
            "1. In your application, go to the \"Bot\" tab in the left sidebar"
        ))
        layout.addWidget(_label(
            "2. Under \"Privileged Gateway Intents\", enable:\n"
            "     \u2022 Message Content Intent\n"
            "     \u2022 Server Members Intent (recommended)"
        ))
        layout.addWidget(_label("3. Click \"Save Changes\""))
        layout.addWidget(_label(
            "4. Click \"Reset Token\" then \"Copy\" to copy your bot token"
        ))
        layout.addWidget(QLabel(""))
        layout.addWidget(_label(
            "\u26a0 Keep your token secret! Never share it publicly."
        ))


class TokenPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Step 3: Enter Your Bot Token")
        layout = QVBoxLayout(self)

        layout.addWidget(_label("Paste your Discord bot token below:"))

        self._token_input = QLineEdit()
        self._token_input.setPlaceholderText("MTIzNDU2Nzg5MDEyMzQ1Njc4OQ...")
        self._token_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self._token_input)

        toggle = QPushButton("Show/hide token")
        toggle.setObjectName("secondary")
        toggle.clicked.connect(self._toggle_visibility)
        layout.addWidget(toggle)

        layout.addWidget(QLabel(""))
        layout.addWidget(_label(
            "\u26a0 Save your token somewhere safe before continuing! "
            "You won't be able to see it again in the Developer Portal."
        ))
        layout.addWidget(_label(
            "Tip: You can always change the token later from the main window."
        ))

        self.registerField("token*", self._token_input)

    def _toggle_visibility(self) -> None:
        if self._token_input.echoMode() == QLineEdit.EchoMode.Password:
            self._token_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self._token_input.setEchoMode(QLineEdit.EchoMode.Password)


class InviteBotPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Step 4: Invite the Bot to Your Server")
        layout = QVBoxLayout(self)

        layout.addWidget(_label(
            "1. In your application, go to \"OAuth2\" \u2192 \"URL Generator\""
        ))
        layout.addWidget(_label("2. Under \"Scopes\", check: bot"))
        layout.addWidget(_label(
            "3. Under \"Bot Permissions\", check:\n"
            "     \u2022 General Permissions \u2192 View Channels\n"
            "     \u2022 Text Permissions \u2192 Read Message History"
        ))
        layout.addWidget(_label(
            "4. Copy the generated URL at the bottom and open it in your browser"
        ))
        layout.addWidget(_label(
            "5. Select your server and authorize the bot"
        ))
        layout.addWidget(_label(
            "\u26a0 Copying this URL will overwrite your clipboard \u2014 "
            "make sure you've saved your token from the previous step first!"
        ))
        layout.addWidget(QLabel(""))
        link = QLabel(
            '<a href="https://discord.com/developers/applications">'
            'Open Developer Portal</a>'
        )
        link.setOpenExternalLinks(True)
        layout.addWidget(link)


class OnboardingWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.info("Creating OnboardingWizard")
        self.setWindowTitle("Disco-Text Setup")
        self.setMinimumSize(550, 420)
        _apply_dark_palette(self)

        pages = [
            WelcomePage(),
            CreateAppPage(),
            CreateBotPage(),
            TokenPage(),
            InviteBotPage(),
        ]
        for page in pages:
            _apply_dark_palette(page)
            self.addPage(page)

        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)

    def get_token(self) -> str:
        return self.field("token") or ""
