#!/usr/bin/env bash

set -euo pipefail

POSTGRES_HOST="${POSTGRES_HOST:-db}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-termopol}"
POSTGRES_USER="${POSTGRES_USER:-admin}"
POSTGRES_SCHEMA="${POSTGRES_SCHEMA:-termopol}"
MIGRATIONS_DIR="${MIGRATIONS_DIR:-/migrations}"

if [[ ! "$POSTGRES_SCHEMA" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
  echo "Invalid POSTGRES_SCHEMA: $POSTGRES_SCHEMA"
  exit 1
fi

export PGPASSWORD="${POSTGRES_PASSWORD:-}"

psql_base=(
  psql
  -h "$POSTGRES_HOST"
  -p "$POSTGRES_PORT"
  -U "$POSTGRES_USER"
  -d "$POSTGRES_DB"
  -v ON_ERROR_STOP=1
  -X
)

echo "Ensuring migration metadata table exists..."
"${psql_base[@]}" <<SQL
CREATE SCHEMA IF NOT EXISTS ${POSTGRES_SCHEMA};
CREATE TABLE IF NOT EXISTS ${POSTGRES_SCHEMA}.schema_migrations (
  filename TEXT PRIMARY KEY,
  checksum TEXT NOT NULL,
  applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
SQL

shopt -s nullglob
migration_files=("$MIGRATIONS_DIR"/*.sql)

if [[ ${#migration_files[@]} -eq 0 ]]; then
  echo "No migration files found in $MIGRATIONS_DIR"
  exit 0
fi

echo "Running migrations from $MIGRATIONS_DIR"
for file in "${migration_files[@]}"; do
  filename="$(basename "$file")"
  checksum="$(shasum -a 256 "$file" | awk '{print $1}')"
  escaped_filename="${filename//\'/\'\'}"

  existing_checksum="$("${psql_base[@]}" -tA -c "SELECT checksum FROM ${POSTGRES_SCHEMA}.schema_migrations WHERE filename = '${escaped_filename}' LIMIT 1;")"

  if [[ -n "$existing_checksum" ]]; then
    if [[ "$existing_checksum" != "$checksum" ]]; then
      echo "Checksum mismatch for already applied migration: $filename"
      echo "Applied: $existing_checksum"
      echo "Current: $checksum"
      exit 1
    fi

    echo "Skipping already applied migration: $filename"
    continue
  fi

  echo "Applying migration: $filename"
  "${psql_base[@]}" -f "$file"
  "${psql_base[@]}" -c "INSERT INTO ${POSTGRES_SCHEMA}.schema_migrations (filename, checksum) VALUES ('${escaped_filename}', '${checksum}');"
done

echo "Migrations completed successfully."
