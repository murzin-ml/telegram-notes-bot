import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from app.api.middlewares.access import AccessMiddleware
from app.api.routing import register_routers
from app.di.container import Container

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


async def main() -> None:
    container = Container()
    settings = container.settings()

    session = AiohttpSession(proxy=settings.telegram_proxy_url or None)
    bot = Bot(token=settings.telegram_token, session=session)
    dispatcher = Dispatcher()

    dispatcher.message.middleware(AccessMiddleware(settings.allowed_ids))
    register_routers(dispatcher)

    dispatcher["note_service"] = container.note_service()
    dispatcher["search_service"] = container.search_service()
    dispatcher["vault"] = container.vault()
    dispatcher["git"] = container.git()

    try:
        await dispatcher.start_polling(bot)
    finally:
        await container.llm_client().aclose()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
