FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml ./

RUN uv pip install --system \
        "numpy>=1.26" "fastapi>=0.111" "uvicorn[standard]>=0.29" \
        "pytest>=8.0" "httpx>=0.27"

COPY src/   ./src/
COPY tests/ ./tests/

ENV PYTHONPATH="/app/src" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "rectangle_analyzer.api:app", "--host", "0.0.0.0", "--port", "8000"]
