FROM python:3.12 AS builder

RUN pip install poetry

WORKDIR /service

COPY pyproject.toml poetry.lock* ./
COPY app /service/app/

RUN poetry config virtualenvs.in-project true
RUN poetry install --without dev

FROM python:3.12-slim

WORKDIR /service

COPY --from=builder /service /service

RUN adduser --disabled-password --gecos '' --no-create-home appuser
RUN chown -R appuser:appuser app/db
USER appuser

EXPOSE 8000

CMD [".venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
