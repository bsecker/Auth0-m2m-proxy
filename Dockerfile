FROM ghcr.io/astral-sh/uv:python3.13-bookworm

WORKDIR /app
COPY . /app

RUN uv sync --locked

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
