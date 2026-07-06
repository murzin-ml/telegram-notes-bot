from app.core.llm.client import LLMClient
from app.core.llm.prompts import ANSWER_SYSTEM
from app.core.search.constants import MAX_CONTEXT_CHARS, NOT_FOUND_REPLY
from app.infra.vault.repository import VaultRepository


class SearchService:
    def __init__(self, vault: VaultRepository, llm: LLMClient) -> None:
        self._vault = vault
        self._llm = llm

    async def answer(self, user_key: str, question: str) -> str:
        notes = self._vault.read_all(user_key)
        if not notes:
            return NOT_FOUND_REPLY
        context = self._build_context(notes)
        return await self._llm.complete(ANSWER_SYSTEM, f"Notes:\n{context}\n\nQuestion: {question}")

    @staticmethod
    def _build_context(notes: list[tuple[str, str]]) -> str:
        blocks: list[str] = []
        total = 0
        for title, text in notes:
            block = f"# {title}\n{text}"
            total += len(block)
            if total > MAX_CONTEXT_CHARS:
                break
            blocks.append(block)
        return "\n\n---\n\n".join(blocks)
