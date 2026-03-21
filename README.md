# termometro-da-polarizacao

## Prerequisites

- Docker + Docker Compose
- Python 3.12+ (for local pipeline execution)
- A configured `.env` file at project root

Expected DB env vars in `.env`:

```env
POSTGRES_DB=termopol
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_PORT=5432
POSTGRES_HOST=localhost
POSTGRES_SCHEMA=termopol
```

Optional cache flags in `.env` (feature flags for tests):

```env
# Disable cache globally (0 or 1)
CACHE_BYPASS=0
```

## Run Database, Redis and API with Docker

From repository root:

```bash
docker compose up -d redis db api
```

The startup flow includes a migration runner (`db-migrations`) that applies all SQL files in `ops/postgres/migrations` before the API starts.

Useful checks:

```bash
docker compose ps
docker compose logs -f redis
docker compose logs -f db
docker compose logs -f api
```

The API uses Redis as a cache layer with a default TTL of 1 day (`86400s`).
You can bypass cache for tests using `.env`:

- `CACHE_BYPASS=1` (disable cache)
- `CACHE_BYPASS=0` (enable cache)

API should be available at:

- `http://localhost:8000`
- `http://localhost:8000/docs`

Health check:

```bash
curl http://localhost:8000/health/
```

Access Postgres shell:

```bash
docker exec -it termopol-db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Stop services:

```bash
docker compose stop redis db api
```

Remove containers (keep DB volume):

```bash
docker compose down
```

Reset database (remove volume and reinitialize schema):

```bash
docker compose down -v --remove-orphans
docker compose up -d redis db api
```

## Database Migrations (Incremental)

- Keep `ops/postgres/init.sql` as bootstrap for brand new volumes only.
- Put every schema change in a new SQL file under `ops/postgres/migrations`.
- Migrations run automatically via `db-migrations` when you start the stack.

Run migrations manually (without starting API):

```bash
docker compose up -d db
docker compose run --rm db-migrations
```

## Run Frontend Locally

The web app lives in `services/web` (Next.js).

### 1) Install dependencies

```bash
cd services/web
npm install
```

### 2) Start dev server

```bash
npm run dev
```

Frontend should be available at:

- `http://localhost:3000`

Notes:

- Run commands inside `services/web` (there is no `package.json` at repo root).
- If you hit engine/dependency errors, use Node `20` LTS (`next@15` requires a newer Node 18+ runtime).

## Run Pipeline

The production runner is:

- `services/pipeline/run.py`

It automatically:

- Determines execution window from `ingestion_log`
- Applies overlap (default `3` days)
- Runs ingest -> transform -> graph -> metrics
- Persists run status as `in_progress` / `completed` / `failed`

### 1) Install pipeline dependencies

```bash
cd services/pipeline
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Execute pipeline

From repository root:

```bash
source services/pipeline/.venv/bin/activate
python services/pipeline/run.py
```

Common options:

```bash
# Increase overlap window
python services/pipeline/run.py --overlap-days 7

# Force a specific period
python services/pipeline/run.py --start-date 2024-01-01 --end-date 2024-06-30

# Verbose logs
python services/pipeline/run.py --verbose
```
