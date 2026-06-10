import discord


def export_md(
    messages: list[discord.Message],
    channel_name: str,
    server_name: str,
) -> str:
    lines: list[str] = []
    lines.append(f"# #{channel_name} — {server_name}")
    lines.append("")
    lines.append(f"**{len(messages)} messages exported**")
    lines.append("")
    lines.append("---")
    lines.append("")

    current_date = None
    for msg in messages:
        msg_date = msg.created_at.strftime("%Y-%m-%d")
        if msg_date != current_date:
            current_date = msg_date
            lines.append(f"## {msg_date}")
            lines.append("")

        timestamp = msg.created_at.strftime("%H:%M")
        author = msg.author.display_name
        content = msg.content or ""
        parts: list[str] = []
        if content:
            parts.append(content)
        for embed in msg.embeds:
            if embed.description:
                parts.append(f"*Embed: {embed.description[:200]}*")
        for att in msg.attachments:
            parts.append(f"*Attachment: [{att.filename}]*")

        joined = " ".join(parts) if parts else "*no content*"
        lines.append(f"**{author}** — {timestamp}")
        lines.append(f"> {joined}")
        lines.append("")

    return "\n".join(lines)
