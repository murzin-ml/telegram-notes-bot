from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    telegram_token: str = Field(alias="TELEGRAM_TOKEN")
    allowed_user_ids: str = Field(default="", alias="ALLOWED_USER_IDS")
    user_vaults: str = Field(default="", alias="USER_VAULTS")
    proxy_url: str = Field(default="", alias="PROXY_URL")
    timezone: str = Field(default="Europe/Moscow", alias="TIMEZONE")

    openrouter_api_key: str = Field(alias="OPENROUTER_API_KEY")
    llm_base_url: str = Field(default="https://openrouter.ai/api/v1", alias="LLM_BASE_URL")
    llm_model: str = Field(default="google/gemini-2.5-flash-lite", alias="LLM_MODEL")

    vault_path: str = Field(alias="VAULT_PATH")
    git_push: bool = Field(default=True, alias="GIT_PUSH")
    reminders_db: str = Field(default="/data/reminders.db", alias="REMINDERS_DB")

    @property
    def allowed_ids(self) -> frozenset[int]:
        return frozenset(int(item) for item in self.allowed_user_ids.split(",") if item.strip())

    @property
    def vault_names(self) -> dict[int, str]:
        names: dict[int, str] = {}
        for pair in self.user_vaults.split(","):
            if ":" in pair:
                uid, name = pair.split(":", 1)
                names[int(uid.strip())] = name.strip()
        return names


@lru_cache
def get_settings() -> Settings:
    return Settings()
