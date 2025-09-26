FROM python:3.12 AS builder

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.in-project true
RUN poetry install --without dev

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app /app

RUN adduser --disabled-password --gecos '' --no-create-home appuser
USER appuser

EXPOSE 8000

CMD [".venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]