import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    ERR_CUSTOMER_NOT_FOUND,
    ERR_INSUFFICIENT_STOCK,
    ERR_NO_WAREHOUSE,
    ERR_PAYMENT_FAILED,
)
from app.domain.order_errors import (
    CreateOrderResult,
    CustomerNotFoundError,
    InsufficientStockError,
    NoWarehouseAvailableError,
    ProductsNotFoundError,
    WarehouseStockUnavailable,
)
from app.models.enums import OrderStatus
from app.models.product import Product
from app.repositories.catalog_repository import CatalogRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.orders import OrderCreateDTO, OrderCreateResponseDTO
from app.services.warehouses import WarehouseService
from app.services.geocoding import GeocodingService
from app.services.idempotency import IdempotencyService
from app.services.inventory import InventoryService
from app.services.payments import PaymentFailedError, PaymentService
from app.utils import aggregate_quantities, calculate_total


class OrderService:
    def __init__(
        self,
        catalog_repository: CatalogRepository | None = None,
        inventory_repository: InventoryRepository | None = None,
        order_repository: OrderRepository | None = None,
        inventory_service: InventoryService | None = None,
        warehouse_service: WarehouseService | None = None,
        geocoding_service: GeocodingService | None = None,
        payment_service: PaymentService | None = None,
        idempotency_service: IdempotencyService | None = None,
    ):
        inventory_repository = inventory_repository or InventoryRepository()
        self.catalog_repository = catalog_repository or CatalogRepository()
        self.order_repository = order_repository or OrderRepository()
        self.inventory_service = inventory_service or InventoryService(inventory_repository)
        self.warehouse_service = warehouse_service or WarehouseService()
        self.geocoding_service = geocoding_service or GeocodingService()
        self.payment_service = payment_service or PaymentService()
        self.idempotency_service = idempotency_service or IdempotencyService()

    async def create_order(
        self,
        db: AsyncSession,
        payload: OrderCreateDTO,
        *,
        idempotency_key: str | None = None,
        idempotency_request_hash: str | None = None,
    ) -> CreateOrderResult:
        quantities_by_product_id = aggregate_quantities(payload.items)

        await self._ensure_customer_exists(db=db, customer_id=payload.customer_id)
        products_by_id = await self._load_products(
            db=db, product_ids=list(quantities_by_product_id.keys())
        )
        total_amount = calculate_total(
            products_by_id=products_by_id,
            quantities_by_product_id=quantities_by_product_id,
        )
        ship_lat, ship_lon = await self.geocoding_service.geocode(payload.shipping_address)
        warehouses_by_distance = await self.warehouse_service.find_fulfilling_by_distance(
            db=db,
            quantities_by_product_id=quantities_by_product_id,
            ship_lat=ship_lat,
            ship_lon=ship_lon,
        )

        if not warehouses_by_distance:
            raise NoWarehouseAvailableError(ERR_NO_WAREHOUSE)

        result: CreateOrderResult | None = None
        chosen_warehouse_id: int | None = None

        for warehouse in warehouses_by_distance:
            try:
                async with db.begin_nested():
                    await self.inventory_service.reserve(
                        db=db,
                        warehouse_id=warehouse.id,
                        quantities_by_product_id=quantities_by_product_id,
                    )
                    order, payment = await self.order_repository.create_pending_order(
                        db=db,
                        customer_id=payload.customer_id,
                        warehouse_id=warehouse.id,
                        total_amount=total_amount,
                        shipping_address=payload.shipping_address,
                        shipping_latitude=ship_lat,
                        shipping_longitude=ship_lon,
                        quantities_by_product_id=quantities_by_product_id,
                        products_by_id=products_by_id,
                    )
                    result = CreateOrderResult(order=order, payment=payment)
                    chosen_warehouse_id = warehouse.id
                break
            except WarehouseStockUnavailable:
                continue

        if result is None or chosen_warehouse_id is None:
            raise InsufficientStockError(ERR_INSUFFICIENT_STOCK)

        await db.commit()

        stripe_idempotency_key = idempotency_key or f"order-{result.order.id}"
        payment_intent = await self.payment_service.create_payment_intent(
            amount=total_amount,
            currency="usd",
            description=f"Order #{result.order.id}",
            metadata={"order_id": str(result.order.id)},
            idempotency_key=stripe_idempotency_key,
        )

        try:
            payment_intent = await self.payment_service.confirm_payment_intent(
                payment_intent_id=payment_intent.id,
                card_number=payload.payment.credit_card_number,
                expiration_date=payload.payment.credit_card_expiration_date,
            )
        except PaymentFailedError:
            await self._release_inventory_on_payment_failure(
                db=db,
                order_id=result.order.id,
                warehouse_id=chosen_warehouse_id,
                quantities_by_product_id=quantities_by_product_id,
                idempotency_key=idempotency_key,
            )
            raise

        return await self._confirm_order(
            db=db,
            order_id=result.order.id,
            payment_intent_id=payment_intent.id,
            idempotency_key=idempotency_key,
            idempotency_request_hash=idempotency_request_hash,
        )

    async def _release_inventory_on_payment_failure(
        self,
        db: AsyncSession,
        order_id: int,
        warehouse_id: int,
        quantities_by_product_id: dict[int, int],
        idempotency_key: str | None = None,
    ) -> None:
        async with db.begin():
            order = await self.order_repository.get_order_for_update(db=db, order_id=order_id)
            if order is None or order.status != OrderStatus.AWAITING_PAYMENT:
                return

            payment = await self.order_repository.get_payment_for_update(db=db, order_id=order_id)
            await self.inventory_service.release(
                db=db,
                warehouse_id=warehouse_id,
                quantities_by_product_id=quantities_by_product_id,
            )
            self.order_repository.mark_failed(order, payment)

        await db.commit()

        if idempotency_key:
            await self.idempotency_service.complete(
                db=db,
                key=idempotency_key,
                response_status=402,
                response_body=json.dumps({"detail": ERR_PAYMENT_FAILED}),
            )

    async def _confirm_order(
        self,
        db: AsyncSession,
        order_id: int,
        payment_intent_id: str,
        idempotency_key: str | None = None,
        idempotency_request_hash: str | None = None,
    ) -> CreateOrderResult:
        async with db.begin():
            order = await self.order_repository.get_order_for_update(db=db, order_id=order_id)
            payment = await self.order_repository.get_payment_for_update(db=db, order_id=order_id)
            self.order_repository.mark_confirmed(order, payment, payment_intent_id)

        await db.commit()

        if idempotency_key and idempotency_request_hash is not None:
            response_dto = OrderCreateResponseDTO(
                order_id=order.id,
                warehouse_id=order.warehouse_id,
                total_amount=order.total_amount,
                status=str(order.status.value),
                payment_status=str(payment.status.value),
            )
            await self.idempotency_service.complete(
                db=db,
                key=idempotency_key,
                response_status=201,
                response_body=response_dto.model_dump_json(),
            )

        return CreateOrderResult(order=order, payment=payment)

    async def _ensure_customer_exists(self, db: AsyncSession, customer_id: int) -> None:
        customer = await self.catalog_repository.get_customer(db=db, customer_id=customer_id)
        if not customer:
            raise CustomerNotFoundError(ERR_CUSTOMER_NOT_FOUND)

    async def _load_products(
        self,
        db: AsyncSession,
        product_ids: list[int],
    ) -> dict[int, Product]:
        rows = await self.catalog_repository.get_products_by_ids(db=db, product_ids=product_ids)
        products_by_id: dict[int, Product] = {product.id: product for product in rows}
        missing_ids = sorted(set(product_ids) - set(products_by_id.keys()))
        if missing_ids:
            raise ProductsNotFoundError(missing_ids)
        return products_by_id
