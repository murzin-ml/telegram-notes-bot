from pydantic import ValidationError

from app.core.llm.client import LLMClient
from app.core.llm.prompts import routing_system
from app.core.llm.schemas import MessageContent, NoteDraftResponse
from app.core.notes.constants import DEFAULT_TITLE, INBOX_FOLDER, JSON_FENCE, SNIPPET_LEN
from app.core.notes.dto import CaptureResult
from app.infra.vault.repository import VaultRepository


class NoteService:
    def __init__(self, llm: LLMClient, vault: VaultRepository) -> None:
        self._llm = llm
        self._vault = vault

    async def capture(self, user_key: str, content: MessageContent) -> CaptureResult:
        folders = self._vault.list_folders(user_key)
        prompt = routing_system(folders, INBOX_FOLDER, self._existing(user_key))
        response = self._parse(await self._llm.complete(prompt, content))

        title = response.title.strip() or DEFAULT_TITLE
        body = response.body.strip()
        target = self._vault.find_note(user_key, response.update_of.strip())
        if target is not None:
            self._vault.overwrite(target, title, body)
            return CaptureResult(folder=target.parent.name, title=title, updated=True)

        folder = response.folder if response.folder in set(folders) | {INBOX_FOLDER} else INBOX_FOLDER
        saved = self._vault.write_note(user_key, folder, title, body)
        return CaptureResult(folder=saved.folder, title=saved.title, updated=False)

    def _existing(self, user_key: str) -> str:
        return "\n".join(
            f"- {title}: {text.strip()[:SNIPPET_LEN]}"
            for title, text in self._vault.read_all(user_key)
        )

    @staticmethod
    def _parse(raw: str) -> NoteDraftResponse:
        cleaned = JSON_FENCE.sub("", raw).strip()
        try:
            return NoteDraftResponse.model_validate_json(cleaned)
        except ValidationError:
            return NoteDraftResponse()
