FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    aiogram \
    openai \
    dependency-injector \
    pydantic-settings \
    aiohttp-socks \
    httpx

COPY app ./app
COPY settings ./settings

CMD ["python", "-m", "app.main"]
