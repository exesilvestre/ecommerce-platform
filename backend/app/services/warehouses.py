from sqlalchemy.ext.asyncio import AsyncSession

from app.models.warehouse import Warehouse
from app.repositories.warehouse_repository import WarehouseRepository
from app.utils import haversine_km


class WarehouseService:
    def __init__(self, warehouse_repository: WarehouseRepository | None = None):
        self.warehouse_repository = warehouse_repository or WarehouseRepository()

    async def find_fulfilling_by_distance(
        self,
        db: AsyncSession,
        quantities_by_product_id: dict[int, int],
        ship_lat: float,
        ship_lon: float,
    ) -> list[Warehouse]:
        warehouses = await self.warehouse_repository.find_with_full_stock(
            db=db,
            quantities_by_product_id=quantities_by_product_id,
        )
        return sorted(
            warehouses,
            key=lambda warehouse: haversine_km(
                ship_lat,
                ship_lon,
                float(warehouse.latitude),
                float(warehouse.longitude),
            ),
        )
