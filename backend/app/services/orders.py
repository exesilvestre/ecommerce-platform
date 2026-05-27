from app.core.constants import ERR_PRODUCTS_NOT_FOUND

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

        async def create_order(self, db: AsyncSession, payload: OrderCreateDTO) -> CreateOrderResult:

            quantities_by_product_id = {item.product_id: int(item.quantity) for item in order.items}
            product_ids = list(quantities_by_product_id.keys())

            await self._ensure_customer_exists(db, payload.customer_id)

            products_by_id = await self._load_products(db, products_ids)

            total_amount = self._calculate_total_amount(products_by_id, quantities_by_product_id)

            ship_lat, ship_lon = await self._geocoding_service.geocode(payload.shipping_address)

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

            async with db.begin():
                chosen_warehouse = await self._reserve_inventory_for_nearest_warehouse(
                    db=db,
                    warehouse_by_distance=warehouses_by_distance,
                    warehouse_by_product_id=warehouses_by_product_id,
                )

                order = Order(
                    customer_id=payload.customer_id,
                    warehouse_id=chosen_warehouse.id,
                    status=OrderStatus.PENDING,
                    total_amount=total_amount,
                    shipping_address=payload.shipping_address,
                    shipping_latitude=ship_lat,
                    shipping_longitude=ship_lng,
                )
                db.add(order)

                await db.flush()

                for product_id, quantity in quantities_by_product_id.items():
                    db.add(
                        OrderItem(
                            order_id = order.id,
                            product_id = product_id,
                            quantity = quantity,
                            unit_price = products_by_id[product_id].price,
                        )
                    )


                payment = Payment(
                    order_id = order.id,
                    amount = total_amount,
                    status = PaymentStatus.PENDING,
                    external_reference = None,
                    credit_card_number = payload.credit_card_number,
                    credit_card_expiration_date = payload.credit_card_expiration_date,
                )
                db.add(payment)

                await db.flush()

                payment_result = await self._payment_service.charge(
                    card_number = payload.credit_card_number,
                    expiration_date = payload.credit_card_expiration_date,
                    amount = total_amount,
                )

                if payment_result.status != PaymentStatus.SUCCESS:
                    # REVIEW
                    order.status = OrderStatus.failed
                    db.add(order)
                    await db.flush()
                    raise PaymentFailedError(ERR_PAYMENT_FAILED)
                
                payment.status = PaymentStatus.SUCCESS
                payment.external_reference = payment_result.external_reference
                order.status = OrderStatus.CONFIRMED


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
        required_products_count = len(quantities_by_product_id)
        inventory_conditions = [
            and_(
                WarehouseInventory.product_id == product_id,
                WarehouseInventory.quantity >= quantity,
            )
            for product_id, quantity in quantities_by_product_id.items()
        ]
        candidate_ids_stmt = (
            select(WarehouseInventory.warehouse_id)
            .where(or_(*inventory_conditions))
            .group_by(WarehouseInventory.warehouse_id)
            .having(
                func.count(func.distinct(WarehouseInventory.product_id))
                == required_products_count
            )
        )
        candidate_ids = (await db.execute(candidate_ids_stmt)).scalars().all()
        if not candidate_ids:
            return []
        warehouses = (
            await db.execute(select(Warehouse).where(Warehouse.id.in_(candidate_ids)))
        ).scalars().all()
        return warehouses


    async def _reserve_inventory_for_nearest_warehouse(
        self,
        db: AsyncSession,
        warehouses_by_distance: list[Warehouse],
        quantities_by_product_id: dict[int, int],
    ) -> Warehouse:
        product_ids = list(quantities_by_product_id.keys())
        for warehouse in warehouses_by_distance:
            inventory_rows = (
                await db.execute(
                    select(WarehouseInventory)
                    .where(
                        WarehouseInventory.warehouse_id == warehouse.id,
                        WarehouseInventory.product_id.in_(product_ids),
                    )
                    .with_for_update()
                )
            ).scalars().all()
            if not self._has_sufficient_stock(inventory_rows, quantities_by_product_id):
                continue
            self._decrement_stock(inventory_rows, quantities_by_product_id)
            return warehouse
        raise InsufficientStockError(ERR_INSUFFICIENT_STOCK)
    
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