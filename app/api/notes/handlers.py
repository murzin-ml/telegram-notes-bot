import base64
import logging
from io import BytesIO

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.api.notes.constants import (
    CAPTURE_HINT,
    ERROR_REPLY,
    HELP_MESSAGE,
    IMAGE_MIME,
    START_MESSAGE,
    VOICE_FORMAT,
)
from app.core.llm.schemas import AudioPart, ImagePart, ImageUrl, InputAudio, MessageContent, TextPart
from app.core.notes.service import NoteService
from app.core.search.service import SearchService
from app.infra.git.sync import GitSync
from app.infra.vault.repository import VaultRepository

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def on_start(message: Message) -> None:
    await message.answer(START_MESSAGE)


@router.message(Command("help"))
async def on_help(message: Message) -> None:
    await message.answer(HELP_MESSAGE)


@router.message(F.text | F.voice | F.photo)
async def on_message(
    message: Message,
    user_key: str,
    note_service: NoteService,
    search_service: SearchService,
    vault: VaultRepository,
    git: GitSync,
) -> None:
    try:
        if _is_question(message):
            await message.answer(await search_service.answer(user_key, message.text))
            return

        draft = await note_service.build_draft(user_key, await _build_content(message))
        saved = vault.write_note(user_key, draft.folder, draft.title, draft.body)
        await git.commit(f"feat(notes): добавил «{saved.title}» в {saved.folder}")
        await message.answer(f"✅ Записал в «{saved.folder}»: {saved.title}")
    except Exception:
        logger.exception("ошибка обработки сообщения")
        await message.answer(ERROR_REPLY)


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
