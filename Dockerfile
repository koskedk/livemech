FROM python:3.12-slim AS builder

# Pin uv version for reproducibility
COPY --from=ghcr.io/astral-sh/uv:0.6.6 /uv /bin/uv

WORKDIR /code

# Use system Python; disable uv-managed Python downloads
ENV UV_PYTHON_DOWNLOADS=never

# Install dependencies (cached layer)
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project --python /usr/local/bin/python3

# Copy application source and install the project
COPY . /code/
RUN uv sync --frozen --no-dev --python /usr/local/bin/python3

# Runtime
FROM python:3.12-slim

RUN useradd --create-home appuser
WORKDIR /code

COPY --from=builder /code/.venv /code/.venv
COPY --from=builder /code/ /code/

ENV PATH="/code/.venv/bin:$PATH"

USER appuser
EXPOSE 8000

CMD ["/code/.venv/bin/uvicorn", "livemech.main:app", "--host", "0.0.0.0", "--port", "8000"]