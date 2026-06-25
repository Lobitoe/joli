# Joli backend — Debian-based Python image with a known-good OpenSSL/TLS stack.
FROM python:3.12-slim

# Cap OpenSSL at TLS 1.2. MongoDB Atlas shared-tier (M0/M2/M5) proxies can
# reject TLS 1.3 handshakes from Linux OpenSSL 3.x with
# "[SSL: TLSV1_ALERT_INTERNAL_ERROR]". Forcing TLS 1.2 avoids it. The app's
# only outbound TLS is to Atlas, so capping the max version is safe here.
RUN sed -i 's/^\[openssl_init\]/[openssl_init]\nssl_conf = ssl_configuration/' /etc/ssl/openssl.cnf \
 && printf '\n[ssl_configuration]\nsystem_default = tls_system_default\n\n[tls_system_default]\nMaxProtocol = TLSv1.2\nCipherString = DEFAULT@SECLEVEL=1\n' >> /etc/ssl/openssl.cnf

WORKDIR /app

# Install Python deps first (better layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . ./

# Render injects $PORT at runtime; default to 8000 for local docker runs.
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
