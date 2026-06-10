import discord


def export_txt(
    messages: list[discord.Message],
    channel_name: str,
    server_name: str,
) -> str:
    lines: list[str] = []
    lines.append(f"# Channel: {channel_name}")
    lines.append(f"# Server: {server_name}")
    lines.append(f"# Messages: {len(messages)}")
    lines.append("")
    for msg in messages:
        timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        author = msg.author.display_name
        content = msg.content or ""
        parts: list[str] = []
        if content:
            parts.append(content)
        for embed in msg.embeds:
            if embed.description:
                parts.append(f"[Embed: {embed.description[:200]}]")
        for att in msg.attachments:
            parts.append(f"[Attachment: {att.filename}]")
        joined = " ".join(parts) if parts else "(no content)"
        lines.append(f"[{author}] {timestamp}")
        lines.append(joined)
        lines.append("")
    return "\n".join(lines)
