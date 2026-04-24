#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${1:-$PROJECT_ROOT/deploy/env/docker.env}"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
DOCKER_CONFIG="${DOCKER_CONFIG:-$HOME/.docker-headless}"
export DOCKER_CONFIG
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0

compose() {
  if docker compose version >/dev/null 2>&1; then
    docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" "$@"
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" "$@"
  else
    echo "ERROR: docker compose is not available." >&2
    exit 1
  fi
}

if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: env file not found: $ENV_FILE" >&2
  echo "Copy deploy/env/docker.env.example to deploy/env/docker.env first." >&2
  exit 1
fi

echo "Using env file: $ENV_FILE"
echo "Project root : $PROJECT_ROOT"

mkdir -p "$DOCKER_CONFIG"
cat > "$DOCKER_CONFIG/config.json" <<'EOF'
{
  "auths": {}
}
EOF

docker info >/dev/null

echo "Building backend image..."
DOCKER_CONFIG="${DOCKER_CONFIG:-$HOME/.docker-headless}"
export DOCKER_CONFIG
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0

docker pull docker.m.daocloud.io/eclipse-temurin:17-jdk-alpine
docker pull docker.m.daocloud.io/eclipse-temurin:17-jre-alpine
docker pull docker.m.daocloud.io/python:3.11-slim
docker pull docker.m.daocloud.io/node:22-alpine
docker pull docker.m.daocloud.io/nginx:1.27-alpine

docker tag docker.m.daocloud.io/eclipse-temurin:17-jdk-alpine campus-runner-base-eclipse-temurin-jdk:17-jdk-alpine
docker tag docker.m.daocloud.io/eclipse-temurin:17-jre-alpine campus-runner-base-eclipse-temurin-jre:17-jre-alpine
docker tag docker.m.daocloud.io/python:3.11-slim campus-runner-base-python:3.11-slim
docker tag docker.m.daocloud.io/node:22-alpine campus-runner-base-node:22-alpine
docker tag docker.m.daocloud.io/nginx:1.27-alpine campus-runner-base-nginx:1.27-alpine

docker build -t campus-runner-backend "$PROJECT_ROOT/backend"

echo "Building ai-rag image..."
docker build -t campus-runner-ai-rag "$PROJECT_ROOT/ai-rag"

echo "Building web image..."
docker build -t campus-runner-web "$PROJECT_ROOT/frontend/web-client"

echo "Starting containers..."
compose up -d --no-build

echo "Checking ChromaDB index..."
if compose exec -T ai-rag sh -c 'test -f /app/data/chroma_db/chroma.sqlite3'; then
  echo "ChromaDB index already exists."
else
  if compose exec -T ai-rag sh -c 'test -n "$ZHIPUAI_API_KEY"'; then
    echo "No ChromaDB index found. Running ingest..."
    compose exec -T ai-rag python src/ingest_data.py
  else
    echo "WARN: ZHIPUAI_API_KEY is empty. Skip ingest_data.py. Rule RAG will stay unavailable until index is built."
  fi
fi

echo "Container status:"
compose ps

echo "Campus Runner Docker deployment is up."
