#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_ENV="$PROJECT_ROOT/deploy/env/backend.env"
SCHEMA_SQL="$PROJECT_ROOT/deploy/sql/schema.sql"

if [ -f "$BACKEND_ENV" ]; then
  set -a
  # shellcheck source=/dev/null
  source "$BACKEND_ENV"
  set +a
fi

DB_NAME="${DB_NAME:-campus_runner}"
DB_USERNAME="${DB_USERNAME:-runner}"
DB_PASSWORD="${DB_PASSWORD:-sc031215}"

echo "Initializing MariaDB database: $DB_NAME"

sudo mariadb <<SQL
CREATE DATABASE IF NOT EXISTS ${DB_NAME} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USERNAME}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
CREATE USER IF NOT EXISTS '${DB_USERNAME}'@'%' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USERNAME}'@'localhost';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USERNAME}'@'%';
FLUSH PRIVILEGES;
SQL

mariadb -u "$DB_USERNAME" -p"$DB_PASSWORD" "$DB_NAME" < "$SCHEMA_SQL"

echo "Database is ready: $DB_NAME / $DB_USERNAME"
