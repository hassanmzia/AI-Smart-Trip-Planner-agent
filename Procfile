# =============================================================================
# Procfile - Process definitions for local development
# =============================================================================
# Used by process managers like honcho, foreman, or overmind.
#
# Install honcho:  pip install honcho
# Run all:         honcho start
# Run specific:    honcho start backend frontend
# =============================================================================

backend: cd backend && ./venv/bin/python manage.py runserver 0.0.0.0:8109
celery-worker: cd backend && ./venv/bin/celery -A travel_agent worker --loglevel=info --concurrency=2
celery-beat: cd backend && ./venv/bin/celery -A travel_agent beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
mcp-server: cd mcp-server && ./venv/bin/python server.py
frontend: cd frontend && npm run dev
