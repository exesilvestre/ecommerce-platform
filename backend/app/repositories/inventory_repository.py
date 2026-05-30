from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse_inventory import WarehouseInventory


class InventoryRepository:
    async def lock_inventory_rows(
        self,
        db: AsyncSession,
        warehouse_id: int,
        product_ids: list[int],
    ) -> list[WarehouseInventory]:
        result = await db.execute(
            select(WarehouseInventory)
            .where(
                WarehouseInventory.warehouse_id == warehouse_id,
                WarehouseInventory.product_id.in_(product_ids),
            )
            .order_by(WarehouseInventory.product_id)
            .with_for_update()
        )
        return list(result.scalars().all())
