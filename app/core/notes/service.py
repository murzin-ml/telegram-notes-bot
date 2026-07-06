from pydantic import ValidationError

from app.core.llm.client import LLMClient
from app.core.llm.prompts import routing_system
from app.core.llm.schemas import MessageContent, NoteDraftResponse
from app.core.notes.constants import DEFAULT_TITLE, INBOX_FOLDER, JSON_FENCE
from app.core.notes.dto import NoteDraft
from app.infra.vault.repository import VaultRepository


class NoteService:
    def __init__(self, llm: LLMClient, vault: VaultRepository) -> None:
        self._llm = llm
        self._vault = vault

    async def build_draft(self, content: MessageContent) -> NoteDraft:
        folders = self._vault.list_folders()
        raw = await self._llm.complete(routing_system(folders, INBOX_FOLDER), content)
        response = self._parse(raw)
        allowed = set(folders) | {INBOX_FOLDER}
        folder = response.folder if response.folder in allowed else INBOX_FOLDER
        title = response.title.strip() or DEFAULT_TITLE
        return NoteDraft(folder=folder, title=title, body=response.body.strip())

    @staticmethod
    def _parse(raw: str) -> NoteDraftResponse:
        cleaned = JSON_FENCE.sub("", raw).strip()
        try:
            return NoteDraftResponse.model_validate_json(cleaned)
        except ValidationError:
            return NoteDraftResponse()
