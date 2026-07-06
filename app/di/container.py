from dependency_injector import containers, providers

from app.core.llm.client import LLMClient
from app.core.notes.service import NoteService
from app.core.search.service import SearchService
from app.infra.git.sync import GitSync
from app.infra.vault.repository import VaultRepository
from settings.config import Settings


class Container(containers.DeclarativeContainer):
    settings = providers.Singleton(Settings)

    llm_client = providers.Singleton(
        LLMClient,
        api_key=settings.provided.openrouter_api_key,
        base_url=settings.provided.llm_base_url,
        model=settings.provided.llm_model,
    )
    vault = providers.Singleton(
        VaultRepository,
        vault_path=settings.provided.vault_path,
    )
    git = providers.Singleton(
        GitSync,
        repo_path=settings.provided.vault_path,
        push=settings.provided.git_push,
    )
    note_service = providers.Singleton(NoteService, llm=llm_client, vault=vault)
    search_service = providers.Singleton(SearchService, vault=vault, llm=llm_client)
