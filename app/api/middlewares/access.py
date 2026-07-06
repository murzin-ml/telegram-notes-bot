from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User


class AccessMiddleware(BaseMiddleware):
    def __init__(self, allowed_ids: frozenset[int], vault_names: dict[int, str]) -> None:
        self._allowed = allowed_ids
        self._vault_names = vault_names

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        if user is None or user.id not in self._allowed:
            return None
        data["user_key"] = self._vault_names.get(user.id, str(user.id))
        return await handler(event, data)
