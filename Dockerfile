FROM python:3.12 AS builder

RUN pip install uv

WORKDIR /service

COPY pyproject.toml uv.lock* ./
COPY app /service/app/

RUN uv sync --no-dev

FROM python:3.12-slim

WORKDIR /service

COPY --from=builder /service /service

RUN adduser --disabled-password --gecos '' --no-create-home appuser
RUN chown -R appuser:appuser app/db
USER appuser

CMD [".venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
LABEL org.opencontainers.image.source=https://github.com/radaron/BackChannelServer