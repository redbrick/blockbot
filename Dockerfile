FROM python:3.14.3-alpine3.23
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --frozen

COPY src src

CMD ["uv", "run", "-m", "src"]
