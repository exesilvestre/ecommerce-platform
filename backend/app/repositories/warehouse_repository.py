from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import Warehouse
from app.models.warehouse_inventory import WarehouseInventory


class WarehouseRepository:
    async def find_with_full_stock(
        self,
        db: AsyncSession,
        quantities_by_product_id: dict[int, int],
    ) -> list[Warehouse]:
        if not quantities_by_product_id:
            return []

        n_products = len(quantities_by_product_id)
        line_conditions = [
            and_(
                WarehouseInventory.product_id == product_id,
                WarehouseInventory.quantity >= quantity,
            )
            for product_id, quantity in quantities_by_product_id.items()
        ]

        eligible_warehouses = (
            select(WarehouseInventory.warehouse_id)
            .where(or_(*line_conditions))
            .group_by(WarehouseInventory.warehouse_id)
            .having(func.count() == n_products)
        ).subquery()

        stmt = select(Warehouse).join(
            eligible_warehouses,
            Warehouse.id == eligible_warehouses.c.warehouse_id,
        )
        return list((await db.execute(stmt)).scalars().all())
