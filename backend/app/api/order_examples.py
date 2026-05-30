"""OpenAPI examples for POST /orders. See SEED_DATA.md for the full scenario guide."""

_PAYMENT_OK = {
    "credit_card_number": "4111111111111111",
    "credit_card_expiration_date": "1228",
}
_PAYMENT_DECLINED = {
    "credit_card_number": "4111111111110000",
    "credit_card_expiration_date": "1228",
}

_AUSTIN = "100 Congress Ave, Austin, TX 78701, USA"
_NYC = "350 5th Ave, New York, NY 10118, USA"


def _order_body(
    *,
    customer_id: int = 1,
    shipping_address: str = _AUSTIN,
    items: list[dict],
    payment: dict | None = None,
) -> dict:
    return {
        "customer_id": customer_id,
        "shipping_address": shipping_address,
        "items": items,
        "payment": payment or _PAYMENT_OK,
    }


ORDER_OPENAPI_EXAMPLES = {
    "happy_path_austin": {
        "summary": "Happy path — ship to Austin",
        "description": "iPhone 16 Pro (product_id=1). Expect 201, warehouse_id=2 (Austin).",
        "value": _order_body(items=[{"product_id": 1, "quantity": 1}]),
    },
    "closest_warehouse_nyc": {
        "summary": "Closest warehouse — ship to NYC",
        "description": "Same product in all warehouses. Expect 201, warehouse_id=3 (New York).",
        "value": _order_body(
            shipping_address=_NYC,
            items=[{"product_id": 1, "quantity": 1}],
        ),
    },
    "multi_item_success": {
        "summary": "Multi-item — iPhone + MacBook to Austin",
        "description": "MacBook only in Cupertino & Austin. Expect 201, warehouse_id=2 (Austin).",
        "value": _order_body(
            items=[
                {"product_id": 1, "quantity": 1},
                {"product_id": 3, "quantity": 1},
            ],
        ),
    },
    "no_warehouse": {
        "summary": "No warehouse — MacBook to NYC",
        "description": "MacBook not stocked in NYC or Miami. Expect 422.",
        "value": _order_body(
            shipping_address=_NYC,
            items=[{"product_id": 3, "quantity": 1}],
        ),
    },
    "payment_declined": {
        "summary": "Payment declined",
        "description": "Cards ending in 0000 are rejected. Expect 402.",
        "value": _order_body(
            items=[{"product_id": 1, "quantity": 1}],
            payment=_PAYMENT_DECLINED,
        ),
    },
    "product_not_found": {
        "summary": "Product not found",
        "description": "Unknown product_id. Expect 404 with missing_product_ids.",
        "value": _order_body(items=[{"product_id": 99999, "quantity": 1}]),
    },
}
