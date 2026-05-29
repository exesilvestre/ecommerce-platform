"""OpenAPI request examples for POST /orders (seed data: customer_id=1, product_id=1 = Linen 3-Seat Sofa)."""

_DEFAULT_ADDRESS = "123 Main St, Austin, TX 78701, USA"
_DEFAULT_PAYMENT = {
    "credit_card_number": "4111111111111111",
    "credit_card_expiration_date": "1228",
}


def _order_body(
    *,
    customer_id: int = 1,
    items: list[dict],
    payment: dict | None = None,
) -> dict:
    return {
        "customer_id": customer_id,
        "shipping_address": _DEFAULT_ADDRESS,
        "items": items,
        "payment": payment or _DEFAULT_PAYMENT,
    }


ORDER_OPENAPI_EXAMPLES = {
    "happy_path": {
        "summary": "Happy path",
        "description": "Valid customer and product from seed. Expect 201 with warehouse_id and total_amount.",
        "value": _order_body(items=[{"product_id": 1, "quantity": 1}]),
    },
    "payment_declined": {
        "summary": "Payment declined",
        "description": "Cards ending in 0000 are rejected by the mock payment API. Expect 402.",
        "value": _order_body(
            items=[{"product_id": 1, "quantity": 1}],
            payment={
                "credit_card_number": "4111111111110000",
                "credit_card_expiration_date": "1228",
            },
        ),
    },
    "customer_not_found": {
        "summary": "Customer not found",
        "description": "Unknown customer_id. Expect 404.",
        "value": _order_body(customer_id=99999, items=[{"product_id": 1, "quantity": 1}]),
    },
    "product_not_found": {
        "summary": "Product not found",
        "description": "Unknown product_id. Expect 404 with missing_product_ids.",
        "value": _order_body(items=[{"product_id": 99999, "quantity": 1}]),
    },
}
