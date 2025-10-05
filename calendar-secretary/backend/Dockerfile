# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

ENV POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential curl && \
    curl -sSL https://install.python-poetry.org | python - --version ${POETRY_VERSION} && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-ansi

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
