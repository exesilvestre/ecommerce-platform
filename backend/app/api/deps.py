from app.repositories.catalog_repository import CatalogRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.warehouse_repository import WarehouseRepository
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
    catalog_repository = CatalogRepository()
    inventory_repository = InventoryRepository()
    return OrderService(
        catalog_repository=catalog_repository,
        inventory_repository=inventory_repository,
        order_repository=OrderRepository(),
        inventory_service=InventoryService(inventory_repository),
        warehouse_service=WarehouseService(WarehouseRepository()),
        geocoding_service=GeocodingService(),
        payment_service=PaymentService(),
        idempotency_service=IdempotencyService(),
    )


def get_product_service() -> ProductService:
    return ProductService()
