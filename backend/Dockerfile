# ── TidalBrix Dummy Backend ──────────────────────────────────────────────
# Mirrors the real backend container but with zero heavy dependencies.
# Base image: slim Python to keep the image small & fast to pull on EC2.
FROM python:3.11-slim

LABEL maintainer="tidalbrix-dummy"
LABEL description="Hello-World dummy of the TidalBrix FastAPI backend"

WORKDIR /app

# Install deps first (Docker layer cache benefit)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY main.py .

# Expose same port as the real backend
EXPOSE 8000

# Health-check (mirrors real deployment pattern)
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run with uvicorn (same as real app)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
