#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/.local/backups"
BACKEND_ENV="$PROJECT_ROOT/deploy/env/backend.env"

mkdir -p "$BACKUP_DIR"

if [ -f "$BACKEND_ENV" ]; then
  set -a
  # shellcheck source=/dev/null
  source "$BACKEND_ENV"
  set +a
fi

echo "Backing up database if mysqldump is available..."
if command -v mysqldump >/dev/null 2>&1; then
  BACKUP_FILE="$BACKUP_DIR/campus_runner_$(date +%Y%m%d_%H%M%S).sql"
  mysqldump -u "${DB_USERNAME:-runner}" -p"${DB_PASSWORD:-sc031215}" campus_runner > "$BACKUP_FILE" || true
  echo "Database backup: $BACKUP_FILE"
else
  echo "WARN: mysqldump not found, skipped database backup."
fi

echo "Pulling latest code..."
cd "$PROJECT_ROOT"
git pull --ff-only

echo "Starting services..."
bash "$PROJECT_ROOT/deploy/orangepi/start-orangepi.sh"
