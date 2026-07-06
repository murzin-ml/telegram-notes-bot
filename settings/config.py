from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    telegram_token: str = Field(alias="TELEGRAM_TOKEN")
    telegram_proxy_url: str = Field(default="", alias="TELEGRAM_PROXY_URL")
    allowed_user_ids: str = Field(default="", alias="ALLOWED_USER_IDS")

    openrouter_api_key: str = Field(alias="OPENROUTER_API_KEY")
    llm_base_url: str = Field(default="https://openrouter.ai/api/v1", alias="LLM_BASE_URL")
    llm_model: str = Field(default="google/gemini-2.5-flash-lite", alias="LLM_MODEL")

    vault_path: str = Field(alias="VAULT_PATH")
    git_push: bool = Field(default=True, alias="GIT_PUSH")

    @property
    def allowed_ids(self) -> frozenset[int]:
        return frozenset(int(item) for item in self.allowed_user_ids.split(",") if item.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()
