FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080

WORKDIR /app

RUN useradd --create-home --uid 10001 appuser && \
    mkdir -p /data

RUN pip install --upgrade --retries 5 pip setuptools wheel

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --retries 5 --no-build-isolation . && \
    python -c "import codereviewer.main" && \
    chown -R appuser:appuser /app /data

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import os, urllib.request; port = os.getenv('PORT', '8080'); urllib.request.urlopen(f'http://127.0.0.1:{port}/healthz', timeout=3).read()" || exit 1

CMD ["python", "-m", "codereviewer.main"]
