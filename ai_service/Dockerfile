# ==============================================================================
# Python AI Microservice Dockerfile for kernel_diagnostic_ai
#
# Provides FastAPI REST interface with RAG vector store and LLM integration.
# ==============================================================================

FROM python:3.12-slim

WORKDIR /app

# Install minimal OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and curated markdown documentation
COPY kernel_diagnostic_ai ./kernel_diagnostic_ai
COPY docs ./docs
COPY main.py ./

# Security: Run as unprivileged non-root user
RUN useradd -m -u 10001 appuser && \
    mkdir -p /app/chroma_data && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8001

HEALTHCHECK --interval=5s --timeout=3s --retries=5 \
  CMD curl -f http://localhost:8001/health || exit 1

CMD ["uvicorn", "kernel_diagnostic_ai.main:app", "--host", "0.0.0.0", "--port", "8001"]
