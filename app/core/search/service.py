import re

from app.core.llm.client import LLMClient
from app.core.llm.prompts import ANSWER_SYSTEM
from app.core.search.constants import MAX_NOTES, MIN_KEYWORD_LEN, NOT_FOUND_REPLY
from app.infra.vault.repository import VaultRepository


class SearchService:
    def __init__(self, vault: VaultRepository, llm: LLMClient) -> None:
        self._vault = vault
        self._llm = llm

    async def answer(self, question: str) -> str:
        notes = self._vault.search(self._keywords(question), limit=MAX_NOTES)
        if not notes:
            return NOT_FOUND_REPLY
        context = "\n\n---\n\n".join(f"# {title}\n{text}" for title, text in notes)
        return await self._llm.complete(ANSWER_SYSTEM, f"Заметки:\n{context}\n\nВопрос: {question}")

    @staticmethod
    def _keywords(question: str) -> list[str]:
        words = re.findall(r"\w+", question.lower())
        return [word for word in words if len(word) >= MIN_KEYWORD_LEN]
