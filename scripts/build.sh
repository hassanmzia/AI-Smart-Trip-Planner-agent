#!/usr/bin/env bash
# build.sh - Resilient Docker build script with retry logic and BuildKit configuration
# Handles Docker Hub metadata loading timeouts by:
#   1. Configuring a BuildKit builder with registry mirrors
#   2. Retrying failed builds with exponential backoff
#   3. Setting extended HTTP timeouts
#
# Usage:
#   ./scripts/build.sh              # Build all services
#   ./scripts/build.sh backend      # Build a specific service
#   ./scripts/build.sh --no-cache   # Build without cache

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILDER_NAME="travel-builder"
BUILDKIT_CONFIG="$PROJECT_DIR/buildkitd.toml"
MAX_RETRIES=3

# Extended timeouts for Docker operations
export COMPOSE_HTTP_TIMEOUT=300
export DOCKER_CLIENT_TIMEOUT=300
export DOCKER_BUILDKIT=1

cd "$PROJECT_DIR"

# --- Helper functions ---

log() {
    echo "[build] $*"
}

error() {
    echo "[build] ERROR: $*" >&2
}

setup_buildx_builder() {
    # Check if our custom builder already exists
    if docker buildx inspect "$BUILDER_NAME" &>/dev/null; then
        log "Using existing BuildKit builder: $BUILDER_NAME"
        docker buildx use "$BUILDER_NAME"
        return 0
    fi

    if [ -f "$BUILDKIT_CONFIG" ]; then
        log "Creating BuildKit builder with registry mirror config..."
        docker buildx create \
            --use \
            --name "$BUILDER_NAME" \
            --config "$BUILDKIT_CONFIG" \
            --driver docker-container \
            --driver-opt network=host \
            2>/dev/null || true
    else
        log "No buildkitd.toml found, using default builder"
    fi
}

pull_with_retry() {
    local image="$1"
    local attempt=1
    local wait_time=2

    while [ $attempt -le $MAX_RETRIES ]; do
        log "Pulling $image (attempt $attempt/$MAX_RETRIES)..."
        if docker pull "$image" 2>/dev/null; then
            log "Successfully pulled $image"
            return 0
        fi
        if [ $attempt -lt $MAX_RETRIES ]; then
            log "Pull failed, retrying in ${wait_time}s..."
            sleep $wait_time
            wait_time=$((wait_time * 2))
        fi
        attempt=$((attempt + 1))
    done

    error "Failed to pull $image after $MAX_RETRIES attempts"
    return 1
}

build_with_retry() {
    local attempt=1
    local wait_time=4

    while [ $attempt -le $MAX_RETRIES ]; do
        log "Build attempt $attempt/$MAX_RETRIES..."
        if docker compose build "$@"; then
            log "Build succeeded"
            return 0
        fi
        if [ $attempt -lt $MAX_RETRIES ]; then
            log "Build failed, retrying in ${wait_time}s..."
            sleep $wait_time
            wait_time=$((wait_time * 2))
        fi
        attempt=$((attempt + 1))
    done

    error "Build failed after $MAX_RETRIES attempts"
    return 1
}

# --- Main ---

log "Setting up BuildKit builder with registry mirrors..."
setup_buildx_builder

# Pre-pull base images with retry logic to warm the cache
log "Pre-pulling base images..."
pull_with_retry "python:3.11-slim" &
pull_with_retry "node:20-alpine" &
pull_with_retry "nginx:alpine" &
wait

log "Starting docker compose build..."
build_with_retry "$@"

log "Build complete. Start services with: docker compose up -d"
