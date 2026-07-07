import asyncio
from collections.abc import Awaitable, Callable

from app.core.llm.schemas import MessageContent, TextPart

FlushCallback = Callable[[str, int, MessageContent], Awaitable[None]]


class CaptureDebouncer:
    def __init__(self, delay: float, on_flush: FlushCallback) -> None:
        self._delay = delay
        self._on_flush = on_flush
        self._buffers: dict[str, list[MessageContent]] = {}
        self._chats: dict[str, int] = {}
        self._tasks: dict[str, asyncio.Task] = {}

    def add(self, user_key: str, chat_id: int, content: MessageContent) -> None:
        self._buffers.setdefault(user_key, []).append(content)
        self._chats[user_key] = chat_id
        task = self._tasks.get(user_key)
        if task is not None:
            task.cancel()
        self._tasks[user_key] = asyncio.create_task(self._flush_later(user_key))

    async def _flush_later(self, user_key: str) -> None:
        try:
            await asyncio.sleep(self._delay)
        except asyncio.CancelledError:
            return
        contents = self._buffers.pop(user_key, [])
        chat_id = self._chats.pop(user_key, None)
        self._tasks.pop(user_key, None)
        if contents and chat_id is not None:
            await self._on_flush(user_key, chat_id, self._merge(contents))

    @staticmethod
    def _merge(contents: list[MessageContent]) -> MessageContent:
        texts: list[str] = []
        media: list = []
        for content in contents:
            if isinstance(content, str):
                if content:
                    texts.append(content)
                continue
            for part in content:
                if isinstance(part, TextPart):
                    if part.text:
                        texts.append(part.text)
                else:
                    media.append(part)
        joined = "\n".join(texts)
        if not media:
            return joined
        parts: list = []
        if joined:
            parts.append(TextPart(text=joined))
        parts.extend(media)
        return parts
