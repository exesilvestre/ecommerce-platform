from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.models.product import Product


class CatalogRepository:
    async def get_customer(self, db: AsyncSession, customer_id: int) -> Customer | None:
        return await db.get(Customer, customer_id)

    async def get_products_by_ids(
        self,
        db: AsyncSession,
        product_ids: list[int],
    ) -> list[Product]:
        if not product_ids:
            return []
        result = await db.execute(select(Product).where(Product.id.in_(product_ids)))
        return list(result.scalars().all())
