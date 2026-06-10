import asyncio
import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class AsyncWorker(Protocol):
    async def run(self) -> None: ...


class DiscordThreadManager:
    def __init__(self) -> None:
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: asyncio.Task | None = None

    def start_loop(self) -> None:
        if self._loop and self._loop.is_running():
            return
        self._loop = asyncio.new_event_loop()

        async def _run_forever() -> None:
            while True:
                await asyncio.sleep(0.1)

        self._thread = asyncio.ensure_future(_run_forever(), loop=self._loop)

        import threading

        def _run() -> None:
            self._loop.run_forever()

        t = threading.Thread(target=_run, daemon=True)
        t.start()

    def stop_loop(self) -> None:
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._loop = None

    def run_coroutine(self, coro):
        if not self._loop or not self._loop.is_running():
            raise RuntimeError("Event loop is not running")
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future

    @property
    def loop(self) -> asyncio.AbstractEventLoop | None:
        return self._loop
