from datetime import datetime, timezone

import discord
import pytest

from src.exporters.txt_exporter import export_txt
from src.exporters.md_exporter import export_md


class FakeUser:
    def __init__(self, name="TestUser"):
        self.display_name = name


class FakeAttachment:
    def __init__(self, filename="image.png"):
        self.filename = filename


class FakeMessage:
    def __init__(self, content, author_name="TestUser", ts=None, embeds=None, attachments=None):
        self.content = content
        self.author = FakeUser(author_name)
        self.created_at = ts or datetime(2026, 6, 10, 12, 0, 0, tzinfo=timezone.utc)
        self.embeds = embeds or []
        self.attachments = attachments or []


def test_txt_export_basic():
    msgs = [
        FakeMessage("Hello world"),
        FakeMessage("Goodbye", author_name="OtherUser"),
    ]
    result = export_txt(msgs, "general", "MyServer")
    assert "# Channel: general" in result
    assert "# Server: MyServer" in result
    assert "[TestUser]" in result
    assert "Hello world" in result
    assert "[OtherUser]" in result
    assert "Goodbye" in result


def test_txt_export_empty():
    result = export_txt([], "general", "MyServer")
    assert "# Messages: 0" in result


def test_md_export_basic():
    msgs = [
        FakeMessage("Hello world"),
        FakeMessage("Goodbye", author_name="OtherUser"),
    ]
    result = export_md(msgs, "general", "MyServer")
    assert "# #general — MyServer" in result
    assert "**TestUser**" in result
    assert "Hello world" in result
    assert "**OtherUser**" in result


def test_md_export_with_attachments():
    msgs = [
        FakeMessage("See this", attachments=[FakeAttachment("photo.png")]),
    ]
    result = export_md(msgs, "general", "MyServer")
    assert "*Attachment: [photo.png]*" in result


def test_txt_export_with_attachment():
    msgs = [
        FakeMessage("", attachments=[FakeAttachment("doc.pdf")]),
    ]
    result = export_txt(msgs, "general", "MyServer")
    assert "[Attachment: doc.pdf]" in result