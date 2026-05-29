# ecommerce-platform

Local stack with Docker Compose: PostgreSQL, FastAPI backend, and Next.js frontend.

## Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (included with Docker Desktop)

## One-command startup

From the repository root:

```bash
docker compose up --build
```

| Service    | URL                          |
|------------|------------------------------|
| Frontend   | http://localhost:3000        |
| API        | http://localhost:8000/health |
| PostgreSQL | localhost:5432               |

On the first run, the backend runs Alembic migrations and loads demo data (`seed/`) only when the database is empty (new Postgres volume).

## Reset the database

To remove the Postgres volume and re-run migrations plus seed:

```bash
docker compose down -v
docker compose up --build
```

## Re-seed manually

```bash
docker compose exec backend python seed/load_seed.py
```

> The seed script **resets** catalog and order tables. Use it only when you want to reload demo data.

## Development without Docker

See `backend/.env.example` for configuration, and set `NEXT_PUBLIC_API_URL=http://localhost:8000` in the frontend before running `npm run dev`.
