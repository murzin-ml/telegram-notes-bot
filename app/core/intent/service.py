from pydantic import ValidationError

from app.core.intent.constants import INTENT_NOTE, INTENTS
from app.core.llm.client import LLMClient
from app.core.llm.prompts import INTENT_SYSTEM
from app.core.llm.schemas import IntentResponse
from app.core.notes.constants import JSON_FENCE


class IntentService:
    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    async def classify(self, text: str) -> str:
        raw = await self._llm.complete(INTENT_SYSTEM, text)
        intent = self._parse(raw).intent
        return intent if intent in INTENTS else INTENT_NOTE

    @staticmethod
    def _parse(raw: str) -> IntentResponse:
        cleaned = JSON_FENCE.sub("", raw).strip()
        try:
            return IntentResponse.model_validate_json(cleaned)
        except ValidationError:
            return IntentResponse()
