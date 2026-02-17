# =============================================================================
# Hugging Face Spaces Dockerfile
# =============================================================================
# Deploys the AI Trip Planner as a single-container app on HF Spaces.
# Uses SQLite for the database and in-memory channels (no Redis/RabbitMQ needed).
#
# HF Spaces Requirements:
#   - Must listen on port 7860
#   - Runs as non-root user (uid=1000)
#   - Persistent storage at /data (optional)
# =============================================================================

FROM python:3.11-slim AS backend-builder

WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt /build/requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder

WORKDIR /build

COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund

COPY frontend/ ./

# Build frontend pointing to the same origin (HF Space serves everything)
ENV VITE_API_URL=""
ENV VITE_WS_URL=""
ENV VITE_MCP_URL="/mcp"
RUN npm run build

# ---------------------------------------------------------------------------
FROM python:3.11-slim

# HF Spaces runs as uid 1000
RUN useradd -m -u 1000 appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=backend-builder /install /usr/local

# Copy backend code
COPY backend/ /app/backend/
WORKDIR /app/backend

# Copy frontend build
COPY --from=frontend-builder /build/dist /app/frontend/dist

# Copy MCP server
COPY mcp-server/ /app/mcp-server/
RUN pip install --no-cache-dir -r /app/mcp-server/requirements.txt

# Create directories
RUN mkdir -p /app/backend/logs /app/backend/staticfiles /app/backend/media /data \
    && chown -R appuser:appuser /app /data

# Nginx configuration for HF Spaces (port 7860)
RUN cat > /etc/nginx/sites-available/default <<'NGINX'
server {
    listen 7860;
    server_name _;
    client_max_body_size 50M;

    # Frontend (static files)
    location / {
        root /app/frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 1d;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8109;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://127.0.0.1:8109;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://127.0.0.1:8109;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # MCP Server
    location /mcp/ {
        proxy_pass http://127.0.0.1:8107/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Static files (Django)
    location /static/ {
        alias /app/backend/staticfiles/;
        expires 30d;
    }

    # Media files
    location /media/ {
        alias /app/backend/media/;
        expires 7d;
    }
}
NGINX

# Supervisor configuration to run all services
RUN cat > /etc/supervisor/conf.d/app.conf <<'SUPERVISOR'
[supervisord]
nodaemon=true
user=root
logfile=/dev/stdout
logfile_maxbytes=0

[program:nginx]
command=nginx -g "daemon off;"
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:backend]
command=gunicorn travel_agent.wsgi:application --bind 127.0.0.1:8109 --workers 2 --timeout 120
directory=/app/backend
user=appuser
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
environment=
    DATABASE_URL="sqlite:////data/db.sqlite3",
    SECRET_KEY="%(ENV_SECRET_KEY)s",
    DEBUG="False",
    ALLOWED_HOSTS="*",
    REDIS_URL="",
    CELERY_BROKER_URL="",
    OPENAI_API_KEY="%(ENV_OPENAI_API_KEY)s",
    SERP_API_KEY="%(ENV_SERP_API_KEY)s",
    STRIPE_SECRET_KEY="%(ENV_STRIPE_SECRET_KEY)s",
    STRIPE_PUBLISHABLE_KEY="%(ENV_STRIPE_PUBLISHABLE_KEY)s",
    WEATHER_API_KEY="%(ENV_WEATHER_API_KEY)s",
    MCP_SERVER_URL="http://127.0.0.1:8107",
    CORS_ALLOWED_ORIGINS="*"

[program:mcp-server]
command=python server.py
directory=/app/mcp-server
user=appuser
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
environment=
    REDIS_URL="",
    MCP_PORT="8107"
SUPERVISOR

# Startup script
RUN cat > /app/start.sh <<'STARTUP'
#!/bin/bash
set -e

# Set defaults for HF Space secrets
export SECRET_KEY="${SECRET_KEY:-hf-space-secret-key-$(date +%s)}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-}"
export SERP_API_KEY="${SERP_API_KEY:-}"
export STRIPE_SECRET_KEY="${STRIPE_SECRET_KEY:-}"
export STRIPE_PUBLISHABLE_KEY="${STRIPE_PUBLISHABLE_KEY:-}"
export WEATHER_API_KEY="${WEATHER_API_KEY:-}"
export DATABASE_URL="sqlite:////data/db.sqlite3"
export REDIS_URL=""
export CELERY_BROKER_URL=""

# Run migrations
cd /app/backend
python manage.py migrate --noinput 2>&1
python manage.py collectstatic --noinput 2>&1 || true

# Create default admin if not exists
python manage.py shell -c "
from apps.users.models import User
if not User.objects.filter(email='admin@trip-planner.com').exists():
    User.objects.create_superuser(email='admin@trip-planner.com', password='admin123', first_name='Admin', last_name='User')
    print('Default admin created: admin@trip-planner.com / admin123')
" 2>&1 || true

# Start supervisor (manages nginx, backend, mcp-server)
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
STARTUP
RUN chmod +x /app/start.sh

EXPOSE 7860

CMD ["/app/start.sh"]
