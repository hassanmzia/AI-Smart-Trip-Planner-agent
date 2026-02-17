#!/usr/bin/env bash
# =============================================================================
# Run AI Trip Planner Locally (Python venv + npm)
# =============================================================================
# This script sets up and runs ALL services without Docker (except optional
# infrastructure services like PostgreSQL, Redis, RabbitMQ).
#
# Usage:
#   ./run-local.sh              # Full setup + run all services
#   ./run-local.sh --setup      # Only setup (install deps, run migrations)
#   ./run-local.sh --backend    # Run only backend + celery
#   ./run-local.sh --frontend   # Run only frontend
#   ./run-local.sh --mcp        # Run only MCP server
#   ./run-local.sh --services   # Start only infra services (Postgres/Redis/RabbitMQ) via Docker
#   ./run-local.sh --stop       # Stop all background processes and infra services
#   ./run-local.sh --sqlite     # Use SQLite instead of PostgreSQL (simplest setup)
# =============================================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"
FRONTEND_DIR="${ROOT_DIR}/frontend"
MCP_DIR="${ROOT_DIR}/mcp-server"
VENV_DIR="${BACKEND_DIR}/venv"
MCP_VENV_DIR="${MCP_DIR}/venv"
PID_DIR="${ROOT_DIR}/.pids"
ENV_FILE="${ROOT_DIR}/.env.local"
USE_SQLITE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }
log_step()  { echo -e "${BLUE}[STEP]${NC}  $*"; }

# ---------------------------------------------------------------------------
# Parse Arguments
# ---------------------------------------------------------------------------
ACTION="all"
for arg in "$@"; do
  case "$arg" in
    --setup)    ACTION="setup" ;;
    --backend)  ACTION="backend" ;;
    --frontend) ACTION="frontend" ;;
    --mcp)      ACTION="mcp" ;;
    --services) ACTION="services" ;;
    --stop)     ACTION="stop" ;;
    --sqlite)   USE_SQLITE=true ;;
    --help|-h)
      head -17 "$0" | tail -14
      exit 0
      ;;
  esac
done

# ---------------------------------------------------------------------------
# Stop all services
# ---------------------------------------------------------------------------
stop_all() {
  log_step "Stopping all services..."

  if [ -d "${PID_DIR}" ]; then
    for pidfile in "${PID_DIR}"/*.pid; do
      [ -f "$pidfile" ] || continue
      pid=$(cat "$pidfile")
      name=$(basename "$pidfile" .pid)
      if kill -0 "$pid" 2>/dev/null; then
        log_info "Stopping ${name} (PID: ${pid})..."
        kill "$pid" 2>/dev/null || true
        # Wait for graceful shutdown
        for i in {1..10}; do
          kill -0 "$pid" 2>/dev/null || break
          sleep 0.5
        done
        # Force kill if still running
        kill -0 "$pid" 2>/dev/null && kill -9 "$pid" 2>/dev/null || true
      fi
      rm -f "$pidfile"
    done
  fi

  # Stop Docker infra services if running
  if docker compose -f "${ROOT_DIR}/docker-compose.services.yml" ps -q 2>/dev/null | grep -q .; then
    log_info "Stopping Docker infrastructure services..."
    docker compose -f "${ROOT_DIR}/docker-compose.services.yml" down
  fi

  log_info "All services stopped."
}

if [ "$ACTION" = "stop" ]; then
  stop_all
  exit 0
fi

# ---------------------------------------------------------------------------
# Environment File
# ---------------------------------------------------------------------------
if [ ! -f "${ENV_FILE}" ]; then
  log_warn "No .env.local found. Creating from template..."
  cp "${ROOT_DIR}/.env.local.example" "${ENV_FILE}"
  if [ "$USE_SQLITE" = true ]; then
    sed -i 's|^DATABASE_URL=postgresql://.*|# DATABASE_URL=postgresql://...\nDATABASE_URL=sqlite:///db.sqlite3|' "${ENV_FILE}" 2>/dev/null || \
    sed -i '' 's|^DATABASE_URL=postgresql://.*|DATABASE_URL=sqlite:///db.sqlite3|' "${ENV_FILE}"
  fi
  log_warn "Edit .env.local with your API keys before running!"
fi

# Export environment variables
set -a
source "${ENV_FILE}"
set +a

# Override for SQLite mode
if [ "$USE_SQLITE" = true ]; then
  export DATABASE_URL="sqlite:///${BACKEND_DIR}/db.sqlite3"
  log_info "Using SQLite database at ${BACKEND_DIR}/db.sqlite3"
fi

# ---------------------------------------------------------------------------
# Check Prerequisites
# ---------------------------------------------------------------------------
check_prereqs() {
  log_step "Checking prerequisites..."

  if ! command -v python3 &>/dev/null; then
    log_error "Python 3 is required but not installed."
    exit 1
  fi
  log_info "Python: $(python3 --version)"

  if ! command -v node &>/dev/null; then
    log_error "Node.js is required but not installed."
    exit 1
  fi
  log_info "Node.js: $(node --version)"

  if ! command -v npm &>/dev/null; then
    log_error "npm is required but not installed."
    exit 1
  fi
  log_info "npm: $(npm --version)"
}

# ---------------------------------------------------------------------------
# Start Infrastructure Services (PostgreSQL, Redis, RabbitMQ via Docker)
# ---------------------------------------------------------------------------
start_infra_services() {
  if [ "$USE_SQLITE" = true ]; then
    log_info "SQLite mode - skipping PostgreSQL Docker container"
  fi

  if command -v docker &>/dev/null && [ "${USE_DOCKER_SERVICES:-true}" = "true" ]; then
    log_step "Starting infrastructure services via Docker..."
    docker compose -f "${ROOT_DIR}/docker-compose.services.yml" up -d

    log_info "Waiting for services to be healthy..."
    local retries=30
    local count=0

    if [ "$USE_SQLITE" != true ]; then
      while ! docker exec trip-planner-postgres pg_isready -U travel_admin -d travel_agent_db -q 2>/dev/null; do
        count=$((count + 1))
        [ $count -ge $retries ] && { log_error "PostgreSQL failed to start"; exit 1; }
        sleep 1
      done
      log_info "PostgreSQL is ready"
    fi

    count=0
    while ! docker exec trip-planner-redis redis-cli -a redis_secure_pass_2026 ping 2>/dev/null | grep -q PONG; do
      count=$((count + 1))
      [ $count -ge $retries ] && { log_warn "Redis not available - some features may be limited"; break; }
      sleep 1
    done
    [ $count -lt $retries ] && log_info "Redis is ready"

    count=0
    while ! docker exec trip-planner-rabbitmq rabbitmq-diagnostics -q ping 2>/dev/null; do
      count=$((count + 1))
      [ $count -ge $retries ] && { log_warn "RabbitMQ not available - Celery tasks disabled"; break; }
      sleep 1
    done
    [ $count -lt $retries ] && log_info "RabbitMQ is ready"
  else
    log_warn "Docker not available. Ensure PostgreSQL, Redis, and RabbitMQ are running locally."
  fi
}

# ---------------------------------------------------------------------------
# Setup Backend (Python venv)
# ---------------------------------------------------------------------------
setup_backend() {
  log_step "Setting up backend (Python virtual environment)..."

  if [ ! -d "${VENV_DIR}" ]; then
    log_info "Creating virtual environment..."
    python3 -m venv "${VENV_DIR}"
  fi

  log_info "Installing Python dependencies..."
  "${VENV_DIR}/bin/pip" install --quiet --upgrade pip
  "${VENV_DIR}/bin/pip" install --quiet -r "${BACKEND_DIR}/requirements.txt"

  # Create required directories
  mkdir -p "${BACKEND_DIR}/logs" "${BACKEND_DIR}/staticfiles" "${BACKEND_DIR}/media"

  log_info "Running database migrations..."
  cd "${BACKEND_DIR}"
  "${VENV_DIR}/bin/python" manage.py migrate --noinput

  log_info "Collecting static files..."
  "${VENV_DIR}/bin/python" manage.py collectstatic --noinput 2>/dev/null || true

  cd "${ROOT_DIR}"
  log_info "Backend setup complete."
}

# ---------------------------------------------------------------------------
# Setup MCP Server (separate venv)
# ---------------------------------------------------------------------------
setup_mcp() {
  log_step "Setting up MCP server..."

  if [ ! -d "${MCP_VENV_DIR}" ]; then
    log_info "Creating MCP virtual environment..."
    python3 -m venv "${MCP_VENV_DIR}"
  fi

  log_info "Installing MCP dependencies..."
  "${MCP_VENV_DIR}/bin/pip" install --quiet --upgrade pip
  "${MCP_VENV_DIR}/bin/pip" install --quiet -r "${MCP_DIR}/requirements.txt"

  log_info "MCP server setup complete."
}

# ---------------------------------------------------------------------------
# Setup Frontend (npm)
# ---------------------------------------------------------------------------
setup_frontend() {
  log_step "Setting up frontend (npm)..."

  cd "${FRONTEND_DIR}"
  if [ ! -d "node_modules" ]; then
    log_info "Installing Node.js dependencies..."
    npm install
  else
    log_info "Node dependencies already installed. Run 'npm install' manually to update."
  fi
  cd "${ROOT_DIR}"

  log_info "Frontend setup complete."
}

# ---------------------------------------------------------------------------
# Run Services
# ---------------------------------------------------------------------------
mkdir -p "${PID_DIR}"

run_backend() {
  log_step "Starting Django backend on port 8109..."
  cd "${BACKEND_DIR}"
  "${VENV_DIR}/bin/python" manage.py runserver 0.0.0.0:8109 &
  echo $! > "${PID_DIR}/backend.pid"
  cd "${ROOT_DIR}"
  log_info "Backend started (PID: $(cat "${PID_DIR}/backend.pid"))"
}

run_celery_worker() {
  log_step "Starting Celery worker..."
  cd "${BACKEND_DIR}"
  "${VENV_DIR}/bin/celery" -A travel_agent worker --loglevel=info --concurrency=2 &
  echo $! > "${PID_DIR}/celery-worker.pid"
  cd "${ROOT_DIR}"
  log_info "Celery worker started (PID: $(cat "${PID_DIR}/celery-worker.pid"))"
}

run_celery_beat() {
  log_step "Starting Celery beat..."
  cd "${BACKEND_DIR}"
  "${VENV_DIR}/bin/celery" -A travel_agent beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler &
  echo $! > "${PID_DIR}/celery-beat.pid"
  cd "${ROOT_DIR}"
  log_info "Celery beat started (PID: $(cat "${PID_DIR}/celery-beat.pid"))"
}

run_mcp() {
  log_step "Starting MCP server on port ${MCP_PORT:-8107}..."
  cd "${MCP_DIR}"
  "${MCP_VENV_DIR}/bin/python" server.py &
  echo $! > "${PID_DIR}/mcp-server.pid"
  cd "${ROOT_DIR}"
  log_info "MCP server started (PID: $(cat "${PID_DIR}/mcp-server.pid"))"
}

run_frontend() {
  log_step "Starting frontend on port 3090..."
  cd "${FRONTEND_DIR}"
  npm run dev &
  echo $! > "${PID_DIR}/frontend.pid"
  cd "${ROOT_DIR}"
  log_info "Frontend started (PID: $(cat "${PID_DIR}/frontend.pid"))"
}

# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------
echo ""
echo "========================================="
echo "  AI Smart Trip Planner - Local Runner"
echo "========================================="
echo ""

case "$ACTION" in
  setup)
    check_prereqs
    start_infra_services
    setup_backend
    setup_mcp
    setup_frontend
    echo ""
    log_info "Setup complete! Run './run-local.sh' to start all services."
    ;;

  services)
    start_infra_services
    echo ""
    log_info "Infrastructure services running."
    log_info "  PostgreSQL: localhost:5432"
    log_info "  Redis:      localhost:6379"
    log_info "  RabbitMQ:   localhost:5672 (Management UI: localhost:15672)"
    ;;

  backend)
    setup_backend
    run_backend
    run_celery_worker
    run_celery_beat
    echo ""
    log_info "Backend services running. Press Ctrl+C to stop."
    wait
    ;;

  frontend)
    setup_frontend
    run_frontend
    echo ""
    log_info "Frontend running at http://localhost:3090. Press Ctrl+C to stop."
    wait
    ;;

  mcp)
    setup_mcp
    run_mcp
    echo ""
    log_info "MCP server running at http://localhost:${MCP_PORT:-8107}. Press Ctrl+C to stop."
    wait
    ;;

  all)
    check_prereqs
    start_infra_services
    setup_backend
    setup_mcp
    setup_frontend

    echo ""
    log_step "Starting all application services..."
    echo ""

    run_backend
    run_celery_worker
    run_celery_beat
    run_mcp
    run_frontend

    echo ""
    echo "========================================="
    echo "  All services are running!"
    echo "========================================="
    echo ""
    echo "  Frontend:       http://localhost:3090"
    echo "  Backend API:    http://localhost:8109/api/"
    echo "  API Docs:       http://localhost:8109/api/docs/"
    echo "  Django Admin:   http://localhost:8109/admin/"
    echo "  MCP Server:     http://localhost:${MCP_PORT:-8107}"
    echo "  RabbitMQ UI:    http://localhost:15672"
    echo ""
    echo "  Stop all:       ./run-local.sh --stop"
    echo ""
    echo "  Press Ctrl+C to stop foreground services..."
    echo "========================================="

    # Wait for all background processes
    trap 'stop_all; exit 0' INT TERM
    wait
    ;;
esac
