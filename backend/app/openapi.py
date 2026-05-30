from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.api.order_examples import ORDER_OPENAPI_EXAMPLES


def _patch_orders_post(schema: dict) -> None:
    orders_post = schema["paths"]["/orders"]["post"]
    request_media = orders_post["requestBody"]["content"]["application/json"]
    request_media["examples"] = ORDER_OPENAPI_EXAMPLES

    responses = orders_post["responses"]

    if "201" in responses:
        media = responses["201"].setdefault("content", {}).setdefault("application/json", {})
        media["example"] = {
            "order_id": 1,
            "warehouse_id": 2,
            "total_amount": "999.00",
            "status": "CONFIRMED",
            "payment_status": "SUCCESS",
        }

    for code, example in {
        "402": {"detail": "Payment failed"},
        "409": {"detail": "Idempotency-Key reused with different request body."},
        "422": {"detail": "No warehouse can fulfill the entire order"},
    }.items():
        if code in responses:
            responses[code].setdefault("content", {}).setdefault("application/json", {})[
                "example"
            ] = example

    if "404" in responses:
        responses["404"].setdefault("content", {}).setdefault("application/json", {})[
            "examples"
        ] = {
            "customer_not_found": {
                "summary": "Customer not found",
                "value": {"detail": "Customer not found"},
            },
            "product_not_found": {
                "summary": "Product not found",
                "value": {
                    "detail": "One or more products were not found",
                    "missing_product_ids": [99999],
                },
            },
        }


def setup_openapi(app: FastAPI) -> None:
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version="1.0.0",
            description=app.description,
            routes=app.routes,
        )
        _patch_orders_post(schema)

        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi
