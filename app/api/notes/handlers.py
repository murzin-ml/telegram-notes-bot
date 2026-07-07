import base64
import logging
from datetime import datetime
from io import BytesIO

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.api.notes.constants import (
    CAPTURE_HINT,
    ERROR_REPLY,
    HELP_MESSAGE,
    IMAGE_MIME,
    NO_REMINDERS,
    REMINDER_FAIL,
    START_MESSAGE,
    VOICE_FORMAT,
)
from app.api.notes.debounce import CaptureDebouncer
from app.core.llm.schemas import AudioPart, ImagePart, ImageUrl, InputAudio, MessageContent, TextPart
from app.core.reminders.constants import RECURRENCE_DAILY, RECURRENCE_WEEKLY, TRIGGER_PREFIXES
from app.core.reminders.dto import Reminder
from app.core.reminders.service import ReminderService
from app.core.search.service import SearchService

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def on_start(message: Message) -> None:
    await message.answer(START_MESSAGE)


@router.message(Command("help"))
async def on_help(message: Message) -> None:
    await message.answer(HELP_MESSAGE)


@router.message(Command("reminders"))
async def on_reminders(message: Message, user_key: str, reminder_service: ReminderService) -> None:
    items = reminder_service.list_active(user_key)
    if not items:
        await message.answer(NO_REMINDERS)
        return
    lines = [f"• {_format_when(item)} — {item.text}" for item in items]
    await message.answer("Твои напоминания:\n" + "\n".join(lines))


@router.message(F.text | F.voice | F.photo)
async def on_message(
    message: Message,
    user_key: str,
    search_service: SearchService,
    reminder_service: ReminderService,
    debouncer: CaptureDebouncer,
) -> None:
    try:
        low = (message.text or "").strip().lower()
        if low and any(low.startswith(prefix) for prefix in TRIGGER_PREFIXES):
            reminder = await reminder_service.create(user_key, message.chat.id, message.text)
            if reminder is None:
                await message.answer(REMINDER_FAIL)
            else:
                await message.answer(f"⏰ Напомню: {reminder.text} — {_format_when(reminder)}")
            return

        if _is_question(message):
            await message.answer(await search_service.answer(user_key, message.text))
            return

        debouncer.add(user_key, message.chat.id, await _build_content(message))
    except Exception:
        logger.exception("ошибка обработки сообщения")
        await message.answer(ERROR_REPLY)


def _format_when(reminder: Reminder) -> str:
    time = reminder.fire_at.strftime("%H:%M")
    if reminder.recurrence == RECURRENCE_DAILY:
        return f"каждый день в {time}"
    if reminder.recurrence == RECURRENCE_WEEKLY:
        return f"каждую неделю, {reminder.fire_at.strftime('%d.%m')} в {time}"
    return reminder.fire_at.strftime("%d.%m в %H:%M")


def _is_question(message: Message) -> bool:
    return bool(message.text) and message.text.strip().endswith("?")


async def _build_content(message: Message) -> MessageContent:
    if message.photo:
        encoded = await _download_b64(message.bot, message.photo[-1].file_id)
        return [
            TextPart(text=message.caption or CAPTURE_HINT),
            ImagePart(image_url=ImageUrl(url=f"data:{IMAGE_MIME};base64,{encoded}")),
        ]
    if message.voice:
        encoded = await _download_b64(message.bot, message.voice.file_id)
        return [
            TextPart(text=CAPTURE_HINT),
            AudioPart(input_audio=InputAudio(data=encoded, format=VOICE_FORMAT)),
        ]
    return message.text or ""


async def _download_b64(bot: Bot, file_id: str) -> str:
    buffer = BytesIO()
    await bot.download(file_id, destination=buffer)
    return base64.b64encode(buffer.getvalue()).decode()
