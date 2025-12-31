# ============================================
# DeepTutor Multi-Stage Dockerfile
# ============================================
# This Dockerfile builds a production-ready image for DeepTutor
# containing both the FastAPI backend and Next.js frontend
#
# Build: docker build -t deeptutor .
# Run:   docker run -p 8001:8001 -p 3782:3782 --env-file .env deeptutor
# ============================================

# ============================================
# Stage 1: Frontend Builder
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/web

# Copy package files first for better caching
COPY web/package.json web/package-lock.json* ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy frontend source code
COPY web/ ./

# Build the Next.js application
# Create a placeholder .env.local for build (will be overridden at runtime)
RUN echo "NEXT_PUBLIC_API_BASE=http://localhost:8001" > .env.local

# Build Next.js for production
RUN npm run build

# ============================================
# Stage 2: Python Base with Dependencies
# ============================================
FROM python:3.11-slim AS python-base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ============================================
# Stage 3: Production Image
# ============================================
FROM python:3.11-slim AS production

# Labels
LABEL maintainer="DeepTutor Team" \
      description="DeepTutor: AI-Powered Personalized Learning Assistant" \
      version="0.1.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    NODE_ENV=production \
    # Default ports (can be overridden)
    BACKEND_PORT=8001 \
    FRONTEND_PORT=3782

WORKDIR /app

# Install Node.js 20.x (LTS) and npm
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    supervisor \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && npm --version

# Copy Python packages from builder stage
COPY --from=python-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-base /usr/local/bin /usr/local/bin

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/web/.next ./web/.next
COPY --from=frontend-builder /app/web/public ./web/public
COPY --from=frontend-builder /app/web/package.json ./web/package.json
COPY --from=frontend-builder /app/web/next.config.js ./web/next.config.js
COPY --from=frontend-builder /app/web/node_modules ./web/node_modules

# Create a startup script for the frontend
RUN echo '#!/bin/bash\ncd /app/web && exec node node_modules/next/dist/bin/next start -H 0.0.0.0 -p ${FRONTEND_PORT:-3782}' > /app/start-frontend.sh && \
    chmod +x /app/start-frontend.sh

# Copy application source code
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/
COPY pyproject.toml ./
COPY requirements.txt ./

# Create necessary directories
RUN mkdir -p \
    data/user/solve \
    data/user/question \
    data/user/research/cache \
    data/user/research/reports \
    data/user/guide \
    data/user/notebook \
    data/user/co-writer/audio \
    data/user/co-writer/tool_calls \
    data/user/logs \
    data/user/run_code_workspace \
    data/user/performance \
    data/knowledge_bases

# Create supervisord configuration for running both services
RUN mkdir -p /etc/supervisor/conf.d

COPY <<EOF /etc/supervisor/conf.d/deeptutor.conf
[supervisord]
nodaemon=true
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid
childlogdir=/var/log/supervisor

[program:backend]
command=python -m uvicorn src.api.main:app --host 0.0.0.0 --port %(ENV_BACKEND_PORT)s
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/backend.err.log
stdout_logfile=/var/log/supervisor/backend.out.log
environment=PYTHONPATH="/app",PYTHONUNBUFFERED="1"

[program:frontend]
command=/bin/bash /app/start-frontend.sh
directory=/app/web
autostart=true
autorestart=true
startsecs=5
stderr_logfile=/var/log/supervisor/frontend.err.log
stdout_logfile=/var/log/supervisor/frontend.out.log
environment=NODE_ENV="production"
EOF

# Create log directories
RUN mkdir -p /var/log/supervisor

# Create entrypoint script
COPY <<'EOF' /app/entrypoint.sh
#!/bin/bash
set -e

echo "============================================"
echo "🚀 Starting DeepTutor"
echo "============================================"

# Set default ports if not provided
export BACKEND_PORT=${BACKEND_PORT:-8001}
export FRONTEND_PORT=${FRONTEND_PORT:-3782}

# Update Next.js environment file with actual backend URL
echo "NEXT_PUBLIC_API_BASE=http://localhost:${BACKEND_PORT}" > /app/web/.env.local

# If NEXT_PUBLIC_API_BASE is provided externally, use it
if [ -n "$NEXT_PUBLIC_API_BASE_EXTERNAL" ]; then
    echo "NEXT_PUBLIC_API_BASE=${NEXT_PUBLIC_API_BASE_EXTERNAL}" > /app/web/.env.local
fi

echo "📌 Backend Port: ${BACKEND_PORT}"
echo "📌 Frontend Port: ${FRONTEND_PORT}"
echo "============================================"

# Check for required environment variables
if [ -z "$LLM_BINDING_API_KEY" ]; then
    echo "⚠️  Warning: LLM_BINDING_API_KEY not set"
    echo "   Please provide LLM configuration via environment variables"
fi

# Start supervisord
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/deeptutor.conf
EOF

RUN chmod +x /app/entrypoint.sh

# Expose ports
EXPOSE 8001 3782

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${BACKEND_PORT:-8001}/ || exit 1

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# ============================================
# Stage 4: Development Image (Optional)
# ============================================
FROM production AS development

# Install development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN pip install --no-cache-dir \
    pre-commit \
    black \
    ruff

# Override supervisord config for development (with reload)
COPY <<EOF /etc/supervisor/conf.d/deeptutor.conf
[supervisord]
nodaemon=true
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid
childlogdir=/var/log/supervisor

[program:backend]
command=python -m uvicorn src.api.main:app --host 0.0.0.0 --port %(ENV_BACKEND_PORT)s --reload
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/backend.err.log
stdout_logfile=/var/log/supervisor/backend.out.log
environment=PYTHONPATH="/app",PYTHONUNBUFFERED="1"

[program:frontend]
command=/bin/bash -c "cd /app/web && node node_modules/next/dist/bin/next dev -H 0.0.0.0 -p ${FRONTEND_PORT:-3782}"
directory=/app/web
autostart=true
autorestart=true
startsecs=5
stderr_logfile=/var/log/supervisor/frontend.err.log
stdout_logfile=/var/log/supervisor/frontend.out.log
environment=NODE_ENV="development"
EOF

# Development ports
EXPOSE 8001 3782
