# ecommerce-platform

Local stack with Docker Compose: PostgreSQL, FastAPI backend, and Next.js frontend.

## Live demo

**[https://ecommerce-platform-eta-sable.vercel.app/](https://ecommerce-platform-eta-sable.vercel.app/)** — add products to the cart, complete checkout, and confirm the order. The header should show **api online**. Card numbers ending in `0000` are declined (demo).

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

See `backend/.env.example` for configuration, and set `API_URL=http://localhost:8000` in `frontend/.env.local` before running `npm run dev`.

## API docs (Swagger)

Interactive docs: **http://localhost:8000/docs**

### How to test

1. Open `POST /orders` → **Try it out**
2. Set header **Idempotency-Key** to a new UUID (generate one per attempt)
3. Pick an example from the **Examples** dropdown
4. Execute

Seed defaults: `customer_id=1`, `product_id=1` (Linen 3-Seat Sofa).

| Example | Expected |
|---------|----------|
| Happy path | 201 — order created with `warehouse_id` |
| Payment declined | 402 — card ending in `0000` |
| Customer not found | 404 |
| Product not found | 404 — includes `missing_product_ids` |
