# Disco-Text

Discord channel text exporter with GUI.

Exports Discord channel messages to `.txt` or `.md` files for easy AI consumption.

## Features

- Browse Discord servers, channels, and messages
- Export messages to plain text or Markdown
- Range and checkbox selection modes
- Message search with match navigation
- 12h/24h clock toggle for message timestamps
- Auto-connect on launch with saved bot token
- Dark theme UI

## Requirements

- Python 3.11+
- A Discord bot token with Message Content Intent enabled

## Install

```
pip install .
```

## Run

```
disco-text
```

On first launch the setup wizard will guide you through creating a bot and entering its token.

## Building

```
pip install pyinstaller
pyinstaller disco-text.spec
```

## License

MIT