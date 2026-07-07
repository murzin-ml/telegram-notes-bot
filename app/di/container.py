from dependency_injector import containers, providers

from app.core.intent.service import IntentService
from app.core.llm.client import LLMClient
from app.core.notes.service import NoteService
from app.core.reminders.service import ReminderService
from app.core.search.service import SearchService
from app.infra.git.sync import GitSync
from app.infra.reminders.storage import ReminderStorage
from app.infra.vault.repository import VaultRepository
from settings.config import Settings


class Container(containers.DeclarativeContainer):
    settings = providers.Singleton(Settings)

    llm_client = providers.Singleton(
        LLMClient,
        api_key=settings.provided.openrouter_api_key,
        base_url=settings.provided.llm_base_url,
        model=settings.provided.llm_model,
        proxy_url=settings.provided.proxy_url,
    )
    vault = providers.Singleton(
        VaultRepository,
        base_path=settings.provided.vault_path,
    )
    git = providers.Singleton(
        GitSync,
        repo_path=settings.provided.vault_path,
        push=settings.provided.git_push,
    )
    reminder_storage = providers.Singleton(
        ReminderStorage,
        db_path=settings.provided.reminders_db,
    )

    intent_service = providers.Singleton(IntentService, llm=llm_client)
    note_service = providers.Singleton(NoteService, llm=llm_client, vault=vault)
    search_service = providers.Singleton(SearchService, vault=vault, llm=llm_client)
    reminder_service = providers.Singleton(
        ReminderService,
        llm=llm_client,
        storage=reminder_storage,
        timezone=settings.provided.timezone,
    )
