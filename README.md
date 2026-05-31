# ecommerce-platform

E-commerce order API built with FastAPI. **The main goal of this project is `POST /orders`** — creating an order with idempotency, warehouse selection, inventory reservation, and mock payment.

The endpoint validates the request, geocodes the shipping address (mock), picks the nearest warehouse that can fulfill the entire order, reserves stock, charges a simulated card, and returns `201`, `402`, `404`, or `422` depending on the scenario. The Next.js frontend is a **checkout test client**; all business logic lives in the backend.

## Live demo

| Resource | URL | Purpose |
|----------|-----|---------|
| **Frontend (Vercel)** | [ecommerce-platform-eta-sable.vercel.app](https://ecommerce-platform-eta-sable.vercel.app/) | Full checkout flow: add products to cart, complete checkout, confirm order. Header shows **api online**. |
| **Swagger (Railway)** | [ecommerce-platform-production-a104.up.railway.app/docs](https://ecommerce-platform-production-a104.up.railway.app/docs) | Test `POST /orders` directly with OpenAPI examples and an `Idempotency-Key`. |

- Card numbers ending in `0000` are declined → **402** (demo).
- Detailed test scenarios, seed data, and demo addresses: **[SEED_DATA.md](SEED_DATA.md)**.
- The Vercel frontend proxies `/api/*` to Railway — you do not need the backend URL to use the web demo.

## Local development

### Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (included with Docker Desktop)

### One command startup

From the repository root:

```bash
docker compose up --build
```

| Service    | URL                          |
|------------|------------------------------|
| Frontend   | http://localhost:3000        |
| API        | http://localhost:8000/health |
| Swagger    | http://localhost:8000/docs     |
| PostgreSQL | localhost:5432               |

On the first run, the backend runs Alembic migrations and loads demo data (`seed/`) only when the database is empty (new Postgres volume).

### Reset the database

To remove the Postgres volume and re-run migrations plus seed:

```bash
docker compose down -v
docker compose up --build
```

### Re-seed manually

Wipes orders, payments, idempotency keys, and reloads all catalog data from `seed.json`:

```bash
docker compose exec backend python seed/load_seed.py
```

> Requires Docker to be running. Does not drop the Postgres volume — use `docker compose down -v` for a full reset.

### Development without Docker

See `backend/.env.example` for configuration, and set `API_URL=http://localhost:8000` in `frontend/.env.local` before running `npm run dev`.

## Documentation

| Doc | Purpose |
|-----|---------|
| [DECISION_LOG.md](DECISION_LOG.md) | Architectural decisions for `POST /orders` (mocks, row locking, idempotency) |
| [SEED_DATA.md](SEED_DATA.md) | Seed catalog, demo addresses, and test scenarios |
| [docs/er-diagram.png](docs/er-diagram.png) | ER diagram — place your PNG in the `docs/` folder |

## For reviewers

Start with **[SEED_DATA.md](SEED_DATA.md)** — seed catalog, demo shipping addresses, and expected outcomes per scenario. For design rationale (why mocks, how row locks work), see **[DECISION_LOG.md](DECISION_LOG.md)**.

**Quick test via Swagger (production or local):**

1. Open Swagger → `POST /orders` → **Try it out**
2. Set **Idempotency-Key** to a new UUID
3. Pick an **Example** → **Execute**

| Demo | Swagger URL |
|------|---------------|
| Production | [Railway /docs](https://ecommerce-platform-production-a104.up.railway.app/docs) |
| Local | http://localhost:8000/docs |

**Quick test via frontend:** [Vercel demo](https://ecommerce-platform-eta-sable.vercel.app/)
