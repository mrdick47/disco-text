import asyncio
import logging
from datetime import datetime
from typing import Protocol

import discord

logger = logging.getLogger(__name__)


class DiscordClientSignals(Protocol):
    def on_connected(self) -> None: ...
    def on_disconnected(self) -> None: ...
    def on_error(self, message: str) -> None: ...


class DiscordClient:
    def __init__(self) -> None:
        self._client: discord.Client | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._connected = False
        self._signals: DiscordClientSignals | None = None

    @property
    def is_connected(self) -> bool:
        return self._connected

    def set_signals(self, signals: DiscordClientSignals) -> None:
        self._signals = signals

    async def connect(self, token: str) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.messages = True

        self._client = discord.Client(intents=intents)

        @self._client.event
        async def on_ready() -> None:
            self._connected = True
            logger.info("Connected as %s", self._client.user)
            if self._signals:
                self._signals.on_connected()

        @self._client.event
        async def on_disconnect() -> None:
            self._connected = False
            if self._signals:
                self._signals.on_disconnected()

        try:
            await self._client.start(token)
        except discord.LoginFailure:
            if self._signals:
                self._signals.on_error("Invalid bot token. Please check your token and try again.")
            raise
        except discord.HTTPException as e:
            if self._signals:
                self._signals.on_error(f"Connection error: {e}")
            raise

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()
            self._connected = False
            self._client = None

    def get_guilds(self) -> list[discord.Guild]:
        if not self._client or not self._connected:
            return []
        return list(self._client.guilds)

    def get_text_channels(self, guild_id: int) -> list[discord.TextChannel]:
        if not self._client or not self._connected:
            logger.warning("get_text_channels called but not connected")
            return []
        guild = self._client.get_guild(guild_id)
        if not guild:
            logger.warning("Guild %s not found", guild_id)
            return []
        if guild.me is None:
            logger.warning(
                "guild.me is None for guild %s, listing all text channels", guild.name
            )
        channels: list[discord.TextChannel] = []
        for category in guild.by_category():
            cat_obj, cat_channels = category
            for ch in cat_channels:
                if isinstance(ch, discord.TextChannel):
                    if guild.me is not None:
                        try:
                            if ch.permissions_for(guild.me).read_messages:
                                channels.append(ch)
                        except Exception:
                            logger.exception("Error checking permissions for #%s", ch.name)
                            channels.append(ch)
                    else:
                        channels.append(ch)
                        logger.debug("Including #%s (no guild.me to check perms)", ch.name)
        logger.info("Found %d text channels in guild %s", len(channels), guild.name)
        return channels

    def get_loop(self) -> asyncio.AbstractEventLoop | None:
        if self._client and self._connected:
            return self._client.loop
        return None

    async def fetch_messages(
        self,
        channel_id: int,
        after: datetime | None = None,
        before: datetime | None = None,
        limit: int | None = None,
        progress_callback=None,
    ) -> list[discord.Message]:
        if not self._client or not self._connected:
            return []

        channel = self._client.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            return []

        kwargs: dict = {}
        if after:
            kwargs["after"] = discord.Object(id=discord.utils.time_snowflake(after))
        if before:
            kwargs["before"] = discord.Object(id=discord.utils.time_snowflake(before))
        if limit is not None:
            kwargs["limit"] = limit
        else:
            kwargs["limit"] = None

        messages = []
        async for message in channel.history(**kwargs):
            messages.append(message)
            if progress_callback and len(messages) % 100 == 0:
                progress_callback(len(messages))

        messages.reverse()
        return messages

    def get_channel_by_id(self, channel_id: int) -> discord.TextChannel | None:
        if not self._client or not self._connected:
            return None
        channel = self._client.get_channel(channel_id)
        if isinstance(channel, discord.TextChannel):
            return channel
        return None
