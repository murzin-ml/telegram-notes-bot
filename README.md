# telegram-notes-bot

A Telegram bot for note-taking: it accepts messages (text, voice, photos) from
whitelisted users, files them into folders in an [Obsidian](https://obsidian.md)
vault and syncs with git. It can search across notes and answer questions.

## About

- **Model:** `google/gemini-2.5-flash-lite` via [OpenRouter](https://openrouter.ai)
  (OpenAI-compatible API) — a single model for text, audio and images.
- **Storage:** a git repository of `.md` files (a clone of an Obsidian vault). Folders are discovered dynamically.
- **Access:** whitelist by Telegram `user_id`.
- **Telegram** is reached through a SOCKS/HTTP proxy (`TELEGRAM_PROXY_URL`); OpenRouter is called directly.

## Stack

- Python 3.12+
- **aiogram** (Telegram Bot API)
- **openai** SDK (with an OpenRouter `base_url`)
- **dependency-injector** (DI)
- Poetry, pytest

## Running

```bash
cp .env.example .env      # fill in tokens, user_id, VAULT_PATH
poetry install
poetry run python -m app.main
```

## Architecture

Feature-sliced clean:

- `app/api/` — Telegram layer (routers, handlers, access middleware).
- `app/core/` — business logic by domain (`notes`, `search`, `llm`).
- `app/infra/` — infrastructure (`vault` — files, `git` — synchronisation).
- `app/di/` — DI container.
- `settings/` — configuration (pydantic-settings).
