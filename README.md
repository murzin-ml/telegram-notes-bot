# telegram-notes-bot

Telegram-бот для заметок: принимает сообщения (текст, голос, фото) от разрешённых
пользователей, раскладывает их по папкам в хранилище [Obsidian](https://obsidian.md)
и синхронизирует с git. Умеет искать по заметкам и отвечать на вопросы.

## О проекте

- **Модель:** `google/gemini-2.5-flash-lite` через [OpenRouter](https://openrouter.ai)
  (OpenAI-совместимый API) — одна модель на текст, аудио и изображения.
- **Хранилище:** git-репозиторий с `.md`-файлами (клон Obsidian-vault). Папки берутся динамически.
- **Доступ:** whitelist по Telegram `user_id`.
- **Telegram** ходит через SOCKS/HTTP-прокси (`TELEGRAM_PROXY_URL`), OpenRouter — напрямую.

## Стек

- Python 3.12+
- **aiogram** (Telegram Bot API)
- **openai** SDK (с `base_url` OpenRouter)
- **dependency-injector** (DI)
- Poetry, pytest

## Запуск

```bash
cp .env.example .env      # заполнить токены, user_id, VAULT_PATH
poetry install
poetry run python -m app.main
```

## Архитектура

Feature-sliced clean:

- `app/api/` — слой Telegram (роутеры, хендлеры, middleware доступа).
- `app/core/` — бизнес-логика по доменам (`notes`, `search`, `llm`).
- `app/infra/` — инфраструктура (`vault` — файлы, `git` — синхронизация).
- `app/di/` — DI-контейнер.
- `settings/` — конфигурация (pydantic-settings).
