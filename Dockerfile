FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir \
    aiogram \
    openai \
    dependency-injector \
    pydantic-settings \
    aiohttp-socks \
    httpx \
    tzdata

COPY app ./app
COPY settings ./settings

CMD ["python", "-m", "app.main"]
