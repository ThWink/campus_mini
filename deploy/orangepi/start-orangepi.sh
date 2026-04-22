#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
AI_DIR="$PROJECT_ROOT/ai-rag"
WEB_DIR="$PROJECT_ROOT/frontend/web-client"

BACKEND_ENV="$PROJECT_ROOT/deploy/env/backend.env"
AI_ENV="$AI_DIR/.env"

wait_port() {
  local port="$1"
  local seconds="${2:-45}"
  local deadline=$((SECONDS + seconds))

  while [ "$SECONDS" -lt "$deadline" ]; do
    if ss -ltn | grep -q ":${port} "; then
      return 0
    fi
    sleep 1
  done

  return 1
}

mkdir -p "$BACKEND_DIR/target" "$AI_DIR/logs"

if [ -f "$BACKEND_ENV" ]; then
  set -a
  # shellcheck source=/dev/null
  source "$BACKEND_ENV"
  set +a
else
  echo "WARN: $BACKEND_ENV not found, using application.yaml or default environment values."
fi

if [ -f "$AI_ENV" ]; then
  set -a
  # shellcheck source=/dev/null
  source "$AI_ENV"
  set +a
else
  echo "WARN: $AI_ENV not found, copy deploy/env/ai-rag.env.example to ai-rag/.env first."
fi

echo "Starting MariaDB and Redis if systemd is available..."
if command -v systemctl >/dev/null 2>&1; then
  sudo systemctl start mariadb || true
  sudo systemctl start redis-server || sudo systemctl start redis || true
fi

echo "Building backend..."
cd "$BACKEND_DIR"
chmod +x ./mvnw || true
./mvnw -DskipTests package

if ! ss -ltn | grep -q ':8080 '; then
  nohup java -jar "$BACKEND_DIR/target/runner-0.0.1-SNAPSHOT.jar" \
    > "$BACKEND_DIR/target/backend.out.log" \
    2> "$BACKEND_DIR/target/backend.err.log" &
fi

wait_port 8080 60 || {
  echo "Backend failed to start. Check backend/target/backend.err.log"
  exit 1
}

echo "Preparing AI/RAG service..."
cd "$AI_DIR"
if [ ! -x ".venv/bin/python" ]; then
  python3 -m venv .venv
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -r requirements.txt
fi

if ! ss -ltn | grep -q ':8000 '; then
  nohup .venv/bin/python src/main.py \
    > "$AI_DIR/logs/fastapi.out.log" \
    2> "$AI_DIR/logs/fastapi.err.log" &
fi

wait_port 8000 60 || {
  echo "AI/RAG failed to start. Check ai-rag/logs/fastapi.err.log"
  exit 1
}

if [ -d "$WEB_DIR" ]; then
  echo "Building web client..."
  cd "$WEB_DIR"
  if [ -f package-lock.json ]; then
    npm ci
  else
    npm install
  fi
  npm run build
fi

echo "Campus Runner is running on Orange Pi:"
echo "  Backend: http://127.0.0.1:8080"
echo "  AI/RAG:  http://127.0.0.1:8000"
echo "  Web dist: frontend/web-client/dist"
