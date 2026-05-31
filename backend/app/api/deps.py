from app.repositories.customer_repository import CustomerRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.warehouse_repository import WarehouseRepository
from app.services.customers import CustomerService
from app.services.geocoding import GeocodingService
from app.services.idempotency import IdempotencyService
from app.services.inventory import InventoryService
from app.services.orders import OrderService
from app.services.payments import PaymentService
from app.services.products import ProductService
from app.services.warehouses import WarehouseService


def get_idempotency_service() -> IdempotencyService:
    return IdempotencyService()


def get_order_service() -> OrderService:
    inventory_repository = InventoryRepository()
    product_service = ProductService(product_repository=ProductRepository())
    customer_service = CustomerService(customer_repository=CustomerRepository())
    return OrderService(
        inventory_repository=inventory_repository,
        product_service=product_service,
        customer_service=customer_service,
        order_repository=OrderRepository(),
        inventory_service=InventoryService(inventory_repository),
        warehouse_service=WarehouseService(WarehouseRepository()),
        geocoding_service=GeocodingService(),
        payment_service=PaymentService(),
        idempotency_service=IdempotencyService(),
    )


def get_product_service() -> ProductService:
    return ProductService(product_repository=ProductRepository())
