# Decision log — `POST /orders`

Technical decisions for the create-order endpoint. Test scenarios: [SEED_DATA.md](SEED_DATA.md).

## Geocoding (mock)

Shipping address is converted to `(lat, lon)` before warehouse selection. A mock `GeocodingService` returns fixed coordinates for four seed addresses and a deterministic hash-based fallback for any other input. The interface is async and swappable for a real provider.

## Payments (mock)

Payment follows a Stripe-like flow: create PaymentIntent, then confirm. The mock stores intents in memory; create is idempotent by key, confirm returns **402** when the card ends in `0000`. Card data is not persisted — only `payment_intent_id` on success.

## Row locking

Stock updates use `SELECT … FOR UPDATE` on `warehouse_inventory` rows before decrement or increment. Product IDs are locked in sorted order to reduce deadlocks on multi-item orders.

Reservation runs inside a savepoint per warehouse attempt. Insufficient stock after lock rolls back the savepoint and tries the next nearest warehouse. On payment failure, stock is restored under the same lock pattern.

Order and payment rows are locked after payment (confirm or failure). The idempotency row is locked on `complete()` to avoid conflicting cached responses on retry.

Warehouse discovery is not locked; races are resolved at reservation time.

## Two-phase commit

Inventory reservation and order creation (`AWAITING_PAYMENT`) are committed before payment. The DB session is closed before the payment call so row locks and connections are not held during external I/O.

Payment outcome is applied in a new session: confirm → `CONFIRMED`, decline → stock released and `FAILED`.

## Warehouse selection

Eligible warehouses must fulfill the entire cart. They are sorted by haversine distance; the nearest is tried first. Each attempt is atomic (savepoint): reserve + pending order. A lost stock race falls through to the next warehouse.

## Idempotency

Requests require an `Idempotency-Key` (UUID) and store a hash of the body. Replays with the same key and body return the cached **201** or **402**. Mismatched body or in-flight request returns **409**.

## Schema

![ER diagram](docs/supabase-schema-gmryjsuyljzxliamvqrd.png)

Core path: `Customer` → `Order` → `OrderItem` / `Payment`; stock via `Warehouse` ↔ `WarehouseInventory` ↔ `Product`. Status: `AWAITING_PAYMENT` → `CONFIRMED` | `FAILED`.
