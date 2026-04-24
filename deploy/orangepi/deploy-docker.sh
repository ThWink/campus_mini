#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${1:-$PROJECT_ROOT/deploy/env/docker.env}"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"

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

docker info >/dev/null

echo "Building and starting containers..."
compose up -d --build

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
