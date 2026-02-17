#!/bin/bash

# Development Setup Script
# Sets up the development environment without Docker
#
# NOTE: For a more comprehensive local setup, use:
#   ./run-local.sh --setup    # Full setup (backend + frontend + MCP server)
#   ./run-local.sh            # Setup and run all services
#   ./run-local.sh --sqlite   # Run with SQLite (no PostgreSQL needed)
#
# See also: make local, make local-setup, make local-sqlite

set -e

echo "========================================="
echo "  AI Travel Agent - Dev Setup           "
echo "========================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "Python version: $(python3 --version)"

# Check Node.js version
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

echo "Node.js version: $(node --version)"

# Create .env.local if missing
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local from template..."
    cp .env.local.example .env.local
    echo "Edit .env.local with your API keys!"
fi

# Setup backend
echo ""
echo "Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create required directories
mkdir -p logs staticfiles media

echo "Running migrations..."
python manage.py migrate

echo "Creating superuser (optional)..."
python manage.py createsuperuser --noinput || true

cd ..

# Setup MCP server
echo ""
echo "Setting up MCP server..."
cd mcp-server

if [ ! -d "venv" ]; then
    echo "Creating MCP virtual environment..."
    python3 -m venv venv
fi

echo "Installing MCP dependencies..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

cd ..

# Setup frontend
echo ""
echo "Setting up frontend..."
cd frontend

echo "Installing Node dependencies..."
npm install

cd ..

echo ""
echo "========================================="
echo "  Development setup complete!           "
echo "========================================="
echo ""
echo "Quick start (recommended):"
echo "  ./run-local.sh              # Run all services"
echo "  ./run-local.sh --sqlite     # Run with SQLite (simplest)"
echo ""
echo "Or run services individually:"
echo ""
echo "To run backend (in backend/ directory):"
echo "  source venv/bin/activate"
echo "  python manage.py runserver 0.0.0.0:8109"
echo ""
echo "To run frontend (in frontend/ directory):"
echo "  npm run dev"
echo ""
echo "To run MCP server (in mcp-server/ directory):"
echo "  ./venv/bin/python server.py"
echo ""
echo "To run Celery worker (in backend/ directory):"
echo "  celery -A travel_agent worker -l info"
echo ""
