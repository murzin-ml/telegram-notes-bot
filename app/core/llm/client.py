from openai import AsyncOpenAI

from app.core.llm.schemas import ChatMessage, ChatRequest, MessageContent


class LLMClient:
    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    async def complete(self, system: str, content: MessageContent) -> str:
        request = ChatRequest(
            model=self._model,
            messages=[
                ChatMessage(role="system", content=system),
                ChatMessage(role="user", content=content),
            ],
        )
        response = await self._client.chat.completions.create(
            **request.model_dump(exclude_none=True),
        )
        return response.choices[0].message.content or ""

    async def aclose(self) -> None:
        await self._client.close()
