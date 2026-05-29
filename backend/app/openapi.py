from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.api.order_examples import ORDER_OPENAPI_EXAMPLES

ORDER_RESPONSE_EXAMPLES = {
    201: {
        "description": "Order created",
        "content": {
            "application/json": {
                "example": {
                    "order_id": 1,
                    "warehouse_id": 2,
                    "total_amount": "899.99",
                    "status": "CONFIRMED",
                    "payment_status": "SUCCESS",
                }
            }
        },
    },
    402: {
        "description": "Payment declined",
        "content": {
            "application/json": {
                "example": {"detail": "Payment failed"}
            }
        },
    },
    404: {
        "description": "Customer or product not found",
        "content": {
            "application/json": {
                "examples": {
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
            }
        },
    },
    409: {
        "description": "Idempotency conflict or request in progress",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Idempotency-Key reused with different request body."
                }
            }
        },
    },
    422: {
        "description": "No warehouse can fulfill the order or insufficient stock",
        "content": {
            "application/json": {
                "example": {"detail": "No warehouse can fulfill the entire order"}
            }
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

        orders_post = schema["paths"]["/orders"]["post"]
        request_media = orders_post["requestBody"]["content"]["application/json"]
        request_media["examples"] = ORDER_OPENAPI_EXAMPLES
        request_media["example"] = ORDER_OPENAPI_EXAMPLES["happy_path"]["value"]

        orders_post["responses"].update(ORDER_RESPONSE_EXAMPLES)

        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi
