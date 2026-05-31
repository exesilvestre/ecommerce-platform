from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.order_errors import WarehouseStockUnavailable
from app.models.warehouse_inventory import WarehouseInventory
from app.repositories.inventory_repository import InventoryRepository


class InventoryService:
    def __init__(self, inventory_repository: InventoryRepository | None = None):
        self.inventory_repository = inventory_repository or InventoryRepository()

    async def reserve(
        self,
        db: AsyncSession,
        warehouse_id: int,
        quantities_by_product_id: dict[int, int],
    ) -> None:
        product_ids = sorted(quantities_by_product_id.keys())
        inventory_rows = await self.inventory_repository.lock_inventory_rows(
            db=db,
            warehouse_id=warehouse_id,
            product_ids=product_ids,
        )
        if not self._has_sufficient_stock(inventory_rows, quantities_by_product_id):
            raise WarehouseStockUnavailable()
        self._decrement_stock(inventory_rows, quantities_by_product_id)

    async def release(
        self,
        db: AsyncSession,
        warehouse_id: int,
        quantities_by_product_id: dict[int, int],
    ) -> None:
        product_ids = sorted(quantities_by_product_id.keys())
        inventory_rows = await self.inventory_repository.lock_inventory_rows(
            db=db,
            warehouse_id=warehouse_id,
            product_ids=product_ids,
        )
        self._increment_stock(inventory_rows, quantities_by_product_id)

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
