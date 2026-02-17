.PHONY: help build up down logs clean restart shell-backend shell-frontend migrate createsuperuser test
.PHONY: local local-setup local-stop local-backend local-frontend local-mcp local-services local-sqlite
.PHONY: hf-deploy

help:
	@echo "AI Travel Agent - Make Commands"
	@echo ""
	@echo "=== Docker Commands ==="
	@echo "  make build              - Build all Docker images"
	@echo "  make up                 - Start all services (Docker)"
	@echo "  make down               - Stop all services (Docker)"
	@echo "  make logs               - View logs from all services"
	@echo "  make clean              - Stop and remove all containers and volumes"
	@echo "  make restart            - Restart all services"
	@echo "  make shell-backend      - Open shell in backend container"
	@echo "  make shell-frontend     - Open shell in frontend container"
	@echo "  make migrate            - Run Django migrations (Docker)"
	@echo "  make createsuperuser    - Create Django superuser (Docker)"
	@echo "  make test               - Run backend tests (Docker)"
	@echo ""
	@echo "=== Local / Virtual Environment Commands ==="
	@echo "  make local              - Run all services locally (venv + npm)"
	@echo "  make local-setup        - Setup only (install deps, run migrations)"
	@echo "  make local-stop         - Stop all local services"
	@echo "  make local-backend      - Run only backend services locally"
	@echo "  make local-frontend     - Run only frontend locally"
	@echo "  make local-mcp          - Run only MCP server locally"
	@echo "  make local-services     - Start only infra (Postgres/Redis/RabbitMQ) via Docker"
	@echo "  make local-sqlite       - Run locally with SQLite (no infra needed)"
	@echo ""
	@echo "=== Deployment Commands ==="
	@echo "  make hf-deploy SPACE=user/name  - Deploy to Hugging Face Spaces"

# =============================================================================
# Docker Commands
# =============================================================================
build:
	docker compose build

up:
	./start.sh

down:
	./stop.sh

logs:
	docker compose logs -f

clean:
	docker compose down -v
	rm -rf backend/staticfiles/*
	rm -rf backend/media/*
	rm -rf frontend/node_modules
	rm -rf frontend/dist

restart:
	docker compose restart

shell-backend:
	docker compose exec backend /bin/bash

shell-frontend:
	docker compose exec frontend /bin/sh

migrate:
	docker compose exec backend python manage.py migrate

createsuperuser:
	docker compose exec backend python manage.py createsuperuser

test:
	docker compose exec backend pytest

collectstatic:
	docker compose exec backend python manage.py collectstatic --noinput

db-reset:
	docker compose down
	docker volume rm ai-smart-flight-agent_postgres_data
	docker compose up -d postgres
	@echo "Waiting for database to be ready..."
	@sleep 10
	docker compose up -d backend
	@sleep 5
	make migrate
	@echo "Database reset complete!"

# =============================================================================
# Local / Virtual Environment Commands
# =============================================================================
local:
	./run-local.sh

local-setup:
	./run-local.sh --setup

local-stop:
	./run-local.sh --stop

local-backend:
	./run-local.sh --backend

local-frontend:
	./run-local.sh --frontend

local-mcp:
	./run-local.sh --mcp

local-services:
	./run-local.sh --services

local-sqlite:
	./run-local.sh --sqlite

# =============================================================================
# Deployment Commands
# =============================================================================
hf-deploy:
	@if [ -z "$(SPACE)" ]; then \
		echo "Usage: make hf-deploy SPACE=username/space-name"; \
		exit 1; \
	fi
	./deploy/huggingface/deploy.sh $(SPACE)
