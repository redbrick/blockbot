FROM python:3.13.2-alpine3.21
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --frozen

COPY src src

CMD ["uv", "run", "-m", "src"]
