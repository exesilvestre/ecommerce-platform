## Quick start

```bash
docker compose up --build
```

| URL | Purpose |
|-----|---------|
| http://localhost:8000/docs | Swagger — test `POST /orders` |
| http://localhost:3000 | Frontend checkout demo |

## Reset database

To wipe orders, payments, idempotency keys, and reload all seed data (Docker must be running):

```bash
docker compose exec backend python seed/load_seed.py
```

This deletes and re-inserts: customers, products, warehouses, inventory, orders, order items, payments, and idempotency keys. IDs restart from 1.

> `docker compose up --build` does **not** reload seed if products already exist. After changing `seed.json`, run `load_seed.py` manually.

**Full reset** (drops the Postgres volume entirely):

```bash
docker compose down -v && docker compose up --build
```

Without Docker (from `backend/`):

```bash
python seed/load_seed.py
```

## Seed data

**Customer:** `customer_id=1` (Alex Rivera)

| product_id | Product | Price |
|------------|---------|-------|
| 1 | iPhone 16 Pro | $999 |
| 2 | AirPods Pro | $249 |
| 3 | MacBook Air 13" M3 | $1,099 |
| 4 | Apple Vision Pro | $3,499 |
| 5 | iPad Pro 13" | $1,299 |
| 6 | Apple Watch Series 10 | $399 |
| 7 | AirTag (4 pack) | $99 |
| 8 | Magic Keyboard for iPad | $349 |

| warehouse_id | Location | Stocks |
|--------------|----------|--------|
| 1 | Cupertino, CA | all 8 products |
| 2 | Austin, TX | iPhone, AirPods, MacBook, Watch, AirTag, Magic Keyboard |
| 3 | New York, NY | iPhone, AirPods, iPad, Watch, AirTag |
| 4 | Miami, FL | iPhone, AirPods, Watch, AirTag |

## Demo shipping addresses

The geocoder is mocked. These four addresses resolve to coords near a warehouse:

| Address | Nearest warehouse |
|---------|-------------------|
| `100 Congress Ave, Austin, TX 78701, USA` | Austin (2) |
| `350 5th Ave, New York, NY 10118, USA` | New York (3) |
| `1 Apple Park Way, Cupertino, CA 95014, USA` | Cupertino (1) |
| `1001 Ocean Dr, Miami Beach, FL 33139, USA` | Miami (4) |

Other addresses use a deterministic hash fallback (not tied to real geography).

## Test scenarios

In Swagger: `POST /orders` → **Try it out** → set **Idempotency-Key** to a new UUID → pick an **Example** → **Execute**.

| Example | Expected |
|---------|----------|
| Happy path — ship to Austin | **201**, `warehouse_id=2` |
| Closest warehouse — ship to NYC | **201**, `warehouse_id=3` |
| Multi-item — iPhone + MacBook to Austin | **201**, `warehouse_id=2` |
| No warehouse — MacBook to NYC | **422** |
| Payment declined | **402** (card ending in `0000`) |
| Product not found | **404** |

## How warehouse selection works

1. Geocode the shipping address.
2. Find warehouses that have **all** requested products in stock.
3. Sort eligible warehouses by distance (haversine).
4. Try the nearest first; reserve inventory and charge payment.

## Payment mock

Any 16-digit card works except numbers ending in `0000` → **402 Payment failed**.
