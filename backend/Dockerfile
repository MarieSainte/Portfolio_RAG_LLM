# Usage: docker-compose up --build

FROM python:3.10-slim

# PYTHONUNBUFFERED : stdout non bufferisé. Sans ça, les logs applicatifs (JSON écrits
# sur stdout) restent coincés dans le buffer Python et n'atteignent jamais Fluentd/Loki
# en temps réel (seul stderr — les barres tqdm — remontait).
# TQDM_DISABLE : coupe les barres de progression "Batches" des modèles ML dans les logs.
ENV PYTHONUNBUFFERED=1 \
    TQDM_DISABLE=1

# Install system dependencies if needed (e.g., for pandas/numpy)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Torch CPU-only en premier (évite les dépendances CUDA — image beaucoup plus légère)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

# Pre-download embedding + reranker models to save time during runtime
RUN python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; \
    SentenceTransformer('all-MiniLM-L6-v2'); \
    CrossEncoder('cross-encoder/mmarco-mMiniLMv2-L12-H384-v1')"

# Copy the rest of the application
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
