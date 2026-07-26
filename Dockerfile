FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt

RUN pip install --upgrade pip \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_sm

FROM python:3.11-slim AS runtime

WORKDIR /app

COPY --from=builder /install /usr/local

COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11

COPY backend/  ./backend/
COPY models/   ./models/
RUN mkdir -p data/raw data/snapshots

RUN adduser --disabled-password --gecos "" appuser \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000 

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5).raise_for_status()"
  
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
