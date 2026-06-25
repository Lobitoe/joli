# Joli backend — runs on a Debian-based Python image with a known-good
# OpenSSL/TLS stack (fixes the Atlas SSL handshake failure seen on Render's
# native from-source Python build).
FROM python:3.12-slim

WORKDIR /app

# Install Python deps first (better layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . ./

# Render injects $PORT at runtime; default to 8000 for local docker runs.
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
