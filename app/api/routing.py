from aiogram import Dispatcher

from app.api.notes.handlers import router as notes_router


def register_routers(dispatcher: Dispatcher) -> None:
    dispatcher.include_router(notes_router)
