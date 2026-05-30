import json
from decimal import Decimal

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    ERR_CUSTOMER_NOT_FOUND,
    ERR_INSUFFICIENT_STOCK,
    ERR_NO_WAREHOUSE,
    ERR_PAYMENT_FAILED,
    ERR_PRODUCTS_NOT_FOUND,
)
from app.models.customer import Customer
from app.models.enums import OrderStatus, PaymentStatus
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.warehouse_inventory import WarehouseInventory
from app.schemas.orders import OrderCreateDTO, OrderCreateResponseDTO
from app.services.geocoding import GeocodingService
from app.services.idempotency import IdempotencyService
from app.services.payments import PaymentFailedError, PaymentService
from app.utils import haversine_km


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


class _WarehouseStockUnavailable(Exception):
    pass


class CreateOrderResult:
    def __init__(self, order: Order, payment: Payment):
        self.order = order
        self.payment = payment


class OrderService:
    def __init__(
        self,
        geocoding_service: GeocodingService | None = None,
        payment_service: PaymentService | None = None,
    ):
        self.geocoding_service = geocoding_service or GeocodingService()
        self.payment_service = payment_service or PaymentService()

    async def create_order(
        self,
        db: AsyncSession,
        payload: OrderCreateDTO,
        *,
        idempotency_key: str | None = None,
        idempotency_request_hash: str | None = None,
    ) -> CreateOrderResult:
        breakpoint()
        quantities_by_product_id: dict[int, int] = {}
        for item in payload.items:
            quantities_by_product_id[item.product_id] = (
                quantities_by_product_id.get(item.product_id, 0) + int(item.quantity)
            )

        await self._ensure_customer_exists(db=db, customer_id=payload.customer_id)
        products_by_id = await self._load_products(
            db=db, product_ids=list(quantities_by_product_id.keys())
        )
        total_amount = self._calculate_total_amount(
            products_by_id=products_by_id,
            quantities_by_product_id=quantities_by_product_id,
        )
        ship_lat, ship_lon = await self.geocoding_service.geocode(payload.shipping_address)
        candidate_warehouses = await self._find_candidate_warehouses(
            db=db,
            quantities_by_product_id=quantities_by_product_id,
        )

        if not candidate_warehouses:
            raise NoWarehouseAvailableError(ERR_NO_WAREHOUSE)

        warehouses_by_distance = sorted(
            candidate_warehouses,
            key=lambda warehouse: haversine_km(
                ship_lat,
                ship_lon,
                float(warehouse.latitude),
                float(warehouse.longitude),
            ),
        )

        result: CreateOrderResult | None = None
        chosen_warehouse_id: int | None = None

        for warehouse in warehouses_by_distance:
            try:
                async with db.begin_nested():
                    result = await self._try_reserve_at_warehouse(
                        db=db,
                        warehouse=warehouse,
                        quantities_by_product_id=quantities_by_product_id,
                        payload=payload,
                        products_by_id=products_by_id,
                        total_amount=total_amount,
                        ship_lat=ship_lat,
                        ship_lon=ship_lon,
                    )
                    chosen_warehouse_id = warehouse.id
                break
            except _WarehouseStockUnavailable:
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

    async def _try_reserve_at_warehouse(
        self,
        db: AsyncSession,
        warehouse: Warehouse,
        quantities_by_product_id: dict[int, int],
        payload: OrderCreateDTO,
        products_by_id: dict[int, Product],
        total_amount: Decimal,
        ship_lat: float,
        ship_lon: float,
    ) -> CreateOrderResult:
        product_ids = sorted(quantities_by_product_id.keys())

        inventory_rows = (
            await db.execute(
                select(WarehouseInventory)
                .where(
                    WarehouseInventory.warehouse_id == warehouse.id,
                    WarehouseInventory.product_id.in_(product_ids),
                )
                .order_by(WarehouseInventory.product_id)
                .with_for_update()
            )
        ).scalars().all()

        if not self._has_sufficient_stock(inventory_rows, quantities_by_product_id):
            raise _WarehouseStockUnavailable()

        self._decrement_stock(inventory_rows, quantities_by_product_id)

        order = Order(
            customer_id=payload.customer_id,
            warehouse_id=warehouse.id,
            status=OrderStatus.AWAITING_PAYMENT,
            total_amount=total_amount,
            shipping_address=payload.shipping_address,
            shipping_latitude=ship_lat,
            shipping_longitude=ship_lon,
        )
        db.add(order)
        await db.flush()

        for product_id, quantity in quantities_by_product_id.items():
            db.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=products_by_id[product_id].price,
                )
            )

        payment = Payment(
            order_id=order.id,
            amount=total_amount,
            status=PaymentStatus.PENDING,
            payment_intent_id=None,
        )
        db.add(payment)
        await db.flush()

        return CreateOrderResult(order=order, payment=payment)

    async def _release_inventory_on_payment_failure(
        self,
        db: AsyncSession,
        order_id: int,
        warehouse_id: int,
        quantities_by_product_id: dict[int, int],
        idempotency_key: str | None = None,
    ) -> None:
        async with db.begin():
            order = await db.get(Order, order_id, with_for_update=True)
            if order is None or order.status != OrderStatus.AWAITING_PAYMENT:
                return

            payment = (
                await db.execute(
                    select(Payment).where(Payment.order_id == order_id).with_for_update()
                )
            ).scalar_one()

            product_ids = sorted(quantities_by_product_id.keys())
            inventory_rows = (
                await db.execute(
                    select(WarehouseInventory)
                    .where(
                        WarehouseInventory.warehouse_id == warehouse_id,
                        WarehouseInventory.product_id.in_(product_ids),
                    )
                    .order_by(WarehouseInventory.product_id)
                    .with_for_update()
                )
            ).scalars().all()

            self._increment_stock(inventory_rows, quantities_by_product_id)
            order.status = OrderStatus.CANCELLED
            payment.status = PaymentStatus.FAILED

        await db.commit()

        if idempotency_key:
            await IdempotencyService().complete(
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
            order = await db.get(Order, order_id, with_for_update=True)
            payment = (
                await db.execute(
                    select(Payment).where(Payment.order_id == order_id).with_for_update()
                )
            ).scalar_one()

            if order.status != OrderStatus.CONFIRMED:
                order.status = OrderStatus.CONFIRMED
                payment.status = PaymentStatus.SUCCESS
                payment.payment_intent_id = payment_intent_id

        await db.commit()

        if idempotency_key and idempotency_request_hash is not None:
            response_dto = OrderCreateResponseDTO(
                order_id=order.id,
                warehouse_id=order.warehouse_id,
                total_amount=order.total_amount,
                status=str(order.status.value),
                payment_status=str(payment.status.value),
            )
            await IdempotencyService().complete(
                db=db,
                key=idempotency_key,
                response_status=201,
                response_body=response_dto.model_dump_json(),
            )

        return CreateOrderResult(order=order, payment=payment)

    async def _ensure_customer_exists(self, db: AsyncSession, customer_id: int) -> None:
        customer = await db.get(Customer, customer_id)
        if not customer:
            raise CustomerNotFoundError(ERR_CUSTOMER_NOT_FOUND)

    async def _load_products(
        self,
        db: AsyncSession,
        product_ids: list[int],
    ) -> dict[int, Product]:
        rows = (
            await db.execute(select(Product).where(Product.id.in_(product_ids)))
        ).scalars().all()
        products_by_id = {product.id: product for product in rows}
        missing_ids = sorted(set(product_ids) - set(products_by_id.keys()))
        if missing_ids:
            raise ProductsNotFoundError(missing_ids)
        return products_by_id

    def _calculate_total_amount(
        self,
        products_by_id: dict[int, Product],
        quantities_by_product_id: dict[int, int],
    ) -> Decimal:
        total = Decimal("0.00")
        for product_id, quantity in quantities_by_product_id.items():
            unit_price = Decimal(str(products_by_id[product_id].price))
            total += unit_price * quantity
        return total

    async def _find_candidate_warehouses(
        self,
        db: AsyncSession,
        quantities_by_product_id: dict[int, int],
    ) -> list[Warehouse]:
        if not quantities_by_product_id:
            return []

        stmt = select(Warehouse)
        for product_id, quantity in quantities_by_product_id.items():
            stmt = stmt.where(
                exists(
                    select(1).where(
                        WarehouseInventory.warehouse_id == Warehouse.id,
                        WarehouseInventory.product_id == product_id,
                        WarehouseInventory.quantity >= quantity,
                    )
                )
            )
        return (await db.execute(stmt)).scalars().all()

    def _has_sufficient_stock(
        self,
        inventory_rows: list[WarehouseInventory],
        quantities_by_product_id: dict[int, int],
    ) -> bool:
        if len(inventory_rows) != len(quantities_by_product_id):
            return False
        inventory_by_product_id = {row.product_id: row for row in inventory_rows}
        for product_id, requested_qty in quantities_by_product_id.items():
            row = inventory_by_product_id.get(product_id)
            if row is None or int(row.quantity) < requested_qty:
                return False
        return True

    def _decrement_stock(
        self,
        inventory_rows: list[WarehouseInventory],
        quantities_by_product_id: dict[int, int],
    ) -> None:
        inventory_by_product_id = {row.product_id: row for row in inventory_rows}
        for product_id, requested_qty in quantities_by_product_id.items():
            row = inventory_by_product_id[product_id]
            row.quantity = int(row.quantity) - requested_qty

    def _increment_stock(
        self,
        inventory_rows: list[WarehouseInventory],
        quantities_by_product_id: dict[int, int],
    ) -> None:
        inventory_by_product_id = {row.product_id: row for row in inventory_rows}
        for product_id, requested_qty in quantities_by_product_id.items():
            row = inventory_by_product_id[product_id]
            row.quantity = int(row.quantity) + requested_qty
