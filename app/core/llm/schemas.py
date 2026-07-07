from pydantic import BaseModel, ConfigDict, Field


class TextPart(BaseModel):
    type: str = Field(default="text", description="Тип части сообщения.")
    text: str = Field(description="Текстовое содержимое.")


class ImageUrl(BaseModel):
    url: str = Field(description="URL или data-URI изображения.")


class ImagePart(BaseModel):
    type: str = Field(default="image_url", description="Тип части сообщения.")
    image_url: ImageUrl = Field(description="Изображение сообщения.")


class InputAudio(BaseModel):
    data: str = Field(description="Аудио в кодировке base64.")
    format: str = Field(description="Формат аудио, например ogg.")


class AudioPart(BaseModel):
    type: str = Field(default="input_audio", description="Тип части сообщения.")
    input_audio: InputAudio = Field(description="Аудио сообщения.")


ContentPart = TextPart | ImagePart | AudioPart
MessageContent = str | list[ContentPart]


class ChatMessage(BaseModel):
    role: str = Field(description="Роль автора сообщения.")
    content: MessageContent = Field(description="Содержимое сообщения.")


class ChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    model: str = Field(description="Имя модели у провайдера.")
    messages: list[ChatMessage] = Field(description="История чата.")
    temperature: float | None = Field(default=None, description="Температура сэмплинга.")
    max_tokens: int | None = Field(default=None, description="Лимит токенов ответа.")


class NoteDraftResponse(BaseModel):
    folder: str = Field(default="", description="Имя папки для заметки.")
    title: str = Field(default="", description="Короткий заголовок заметки.")
    body: str = Field(default="", description="Текст заметки.")
    update_of: str = Field(
        default="",
        description="Заголовок существующей заметки, которую нужно обновить, или пусто для новой.",
    )


class ReminderParseResponse(BaseModel):
    text: str = Field(default="", description="Что напомнить, коротко.")
    at: str = Field(default="", description="Первое срабатывание, ISO 8601 без таймзоны.")
    recurrence: str = Field(default="none", description="Повтор: none, daily или weekly.")
