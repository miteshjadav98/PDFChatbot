# ============================================================
# Stage 1: Builder — install Python deps in a virtual env
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /app

# System deps needed to compile some Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install Python deps (CPU-only PyTorch via extra index)
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================
# Stage 2: Runtime — lean image with only what's needed
# ============================================================
FROM python:3.11-slim

WORKDIR /app

# Runtime system deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends supervisor && \
    rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY .streamlit/ ./.streamlit/
COPY supervisord.conf ./supervisord.conf

# Create directories for runtime data
RUN mkdir -p faiss_index session_stores /var/log

# Expose Streamlit (primary ingress) and FastAPI (internal)
EXPOSE 8501 8000

# Health check — hit FastAPI's /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run both services via supervisord
CMD ["supervisord", "-c", "supervisord.conf"]
