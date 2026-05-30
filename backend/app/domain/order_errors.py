from app.core.constants import ERR_PRODUCTS_NOT_FOUND
from app.models.order import Order
from app.models.payment import Payment


class OrderServiceError(Exception):
    pass


class CustomerNotFoundError(OrderServiceError):
    pass


class ProductsNotFoundError(OrderServiceError):
    def __init__(self, missing_product_ids: list[int]):
        self.missing_product_ids = missing_product_ids
        super().__init__(ERR_PRODUCTS_NOT_FOUND)


class NoWarehouseAvailableError(OrderServiceError):
    pass


class InsufficientStockError(OrderServiceError):
    pass


class WarehouseStockUnavailable(Exception):
    pass


class CreateOrderResult:
    def __init__(self, order: Order, payment: Payment):
        self.order = order
        self.payment = payment
