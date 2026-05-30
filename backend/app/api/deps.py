from app.services.idempotency import IdempotencyService
from app.services.orders import OrderService
from app.services.products import ProductService


def get_idempotency_service() -> IdempotencyService:
    return IdempotencyService()


def get_order_service() -> OrderService:
    return OrderService()


def get_product_service() -> ProductService:
    return ProductService()
