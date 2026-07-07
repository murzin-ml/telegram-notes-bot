from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from pydantic import ValidationError

from app.core.llm.client import LLMClient
from app.core.llm.prompts import reminder_parse_system
from app.core.llm.schemas import ReminderParseResponse
from app.core.notes.constants import JSON_FENCE
from app.core.reminders.constants import (
    RECURRENCE_DAILY,
    RECURRENCE_NONE,
    RECURRENCE_WEEKLY,
    RECURRENCES,
)
from app.core.reminders.dto import Reminder
from app.infra.reminders.storage import ReminderStorage


class ReminderService:
    def __init__(self, llm: LLMClient, storage: ReminderStorage, timezone: str) -> None:
        self._llm = llm
        self._storage = storage
        self._tz = ZoneInfo(timezone)

    def now(self) -> datetime:
        return datetime.now(self._tz).replace(tzinfo=None)

    async def create(self, user_key: str, chat_id: int, message_text: str) -> Reminder | None:
        raw = await self._llm.complete(reminder_parse_system(self.now().isoformat()), message_text)
        parsed = self._parse(raw)
        fire_at = self._to_datetime(parsed.at)
        if fire_at is None or not parsed.text.strip():
            return None
        recurrence = parsed.recurrence if parsed.recurrence in RECURRENCES else RECURRENCE_NONE
        return self._storage.add(user_key, chat_id, parsed.text.strip(), fire_at, recurrence)

    def due(self) -> list[Reminder]:
        return self._storage.due(self.now())

    def list_active(self, user_key: str) -> list[Reminder]:
        return self._storage.list_active(user_key)

    def advance(self, reminder: Reminder) -> None:
        if reminder.recurrence == RECURRENCE_NONE:
            self._storage.close(reminder.id)
            return
        step = timedelta(days=1) if reminder.recurrence == RECURRENCE_DAILY else timedelta(weeks=1)
        next_at = reminder.fire_at + step
        now = self.now()
        while next_at <= now:
            next_at += step
        self._storage.reschedule(reminder.id, next_at)

    @staticmethod
    def _parse(raw: str) -> ReminderParseResponse:
        cleaned = JSON_FENCE.sub("", raw).strip()
        try:
            return ReminderParseResponse.model_validate_json(cleaned)
        except ValidationError:
            return ReminderParseResponse()

    @staticmethod
    def _to_datetime(value: str) -> datetime | None:
        try:
            return datetime.fromisoformat(value).replace(tzinfo=None)
        except (ValueError, TypeError):
            return None
