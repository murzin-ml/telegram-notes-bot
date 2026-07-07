import base64
import logging
from io import BytesIO

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.api.notes.constants import (
    CAPTURE_HINT,
    DELETE_NONE,
    ERROR_REPLY,
    HELP_MESSAGE,
    IMAGE_MIME,
    NO_REMINDERS,
    REMINDER_FAIL,
    START_MESSAGE,
    VOICE_FORMAT,
)
from app.api.notes.debounce import CaptureDebouncer
from app.core.intent.constants import INTENT_DELETE, INTENT_QUESTION, INTENT_REMINDER
from app.core.intent.service import IntentService
from app.core.llm.schemas import AudioPart, ImagePart, ImageUrl, InputAudio, MessageContent, TextPart
from app.core.notes.service import NoteService
from app.core.reminders.constants import RECURRENCE_DAILY, RECURRENCE_WEEKLY
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
    intent_service: IntentService,
    note_service: NoteService,
    search_service: SearchService,
    reminder_service: ReminderService,
    debouncer: CaptureDebouncer,
) -> None:
    try:
        if message.voice or message.photo:
            debouncer.add(user_key, message.chat.id, await _build_content(message))
            return

        text = (message.text or "").strip()
        if not text:
            return

        intent = await intent_service.classify(text)
        if intent == INTENT_REMINDER:
            reminder = await reminder_service.create(user_key, message.chat.id, text)
            if reminder is None:
                await message.answer(REMINDER_FAIL)
            else:
                await message.answer(f"⏰ Напомню: {reminder.text} — {_format_when(reminder)}")
            return

        if intent == INTENT_DELETE:
            deleted = await note_service.forget(user_key, text)
            if deleted:
                await message.answer("🗑 Удалил: " + ", ".join(deleted))
            else:
                await message.answer(DELETE_NONE)
            return

        if intent == INTENT_QUESTION:
            await message.answer(await search_service.answer(user_key, text))
            return

        debouncer.add(user_key, message.chat.id, text)
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
