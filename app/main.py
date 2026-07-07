import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import BotCommand

from app.api.middlewares.access import AccessMiddleware
from app.api.notes.constants import ERROR_REPLY
from app.api.notes.debounce import CaptureDebouncer
from app.api.routing import register_routers
from app.core.reminders.constants import TICK_SECONDS
from app.di.container import Container

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

_CAPTURE_DELAY = 2.0
_COMMANDS = [
    BotCommand(command="start", description="Приветствие"),
    BotCommand(command="help", description="Как пользоваться"),
    BotCommand(command="reminders", description="Список напоминаний"),
]


async def main() -> None:
    container = Container()
    settings = container.settings()
    note_service = container.note_service()
    git = container.git()
    reminder_service = container.reminder_service()

    session = AiohttpSession(proxy=settings.proxy_url or None)
    bot = Bot(token=settings.telegram_token, session=session)
    dispatcher = Dispatcher()

    async def capture_flush(user_key: str, chat_id: int, content) -> None:
        try:
            result = await note_service.capture(user_key, content)
            action = "обновил" if result.updated else "добавил"
            await git.commit(f"feat(notes): {action} «{result.title}» в {result.folder}")
            reply = "Обновил" if result.updated else "Записал"
            await bot.send_message(chat_id, f"✅ {reply} в «{result.folder}»: {result.title}")
        except Exception:
            logger.exception("ошибка захвата")
            await bot.send_message(chat_id, ERROR_REPLY)

    debouncer = CaptureDebouncer(_CAPTURE_DELAY, capture_flush)

    dispatcher.message.middleware(AccessMiddleware(settings.allowed_ids, settings.vault_names))
    register_routers(dispatcher)
    dispatcher["intent_service"] = container.intent_service()
    dispatcher["note_service"] = note_service
    dispatcher["search_service"] = container.search_service()
    dispatcher["reminder_service"] = reminder_service
    dispatcher["debouncer"] = debouncer

    await bot.set_my_commands(_COMMANDS)
    scheduler = asyncio.create_task(_reminder_loop(bot, reminder_service))
    try:
        await dispatcher.start_polling(bot)
    finally:
        scheduler.cancel()
        await container.llm_client().aclose()
        await bot.session.close()


async def _reminder_loop(bot: Bot, reminder_service) -> None:
    while True:
        await asyncio.sleep(TICK_SECONDS)
        try:
            due = reminder_service.due()
        except Exception:
            logger.exception("ошибка чтения напоминаний")
            continue
        for reminder in due:
            try:
                await bot.send_message(reminder.chat_id, f"⏰ Напоминание: {reminder.text}")
            except Exception:
                logger.exception("не удалось отправить напоминание")
            reminder_service.advance(reminder)


if __name__ == "__main__":
    asyncio.run(main())
