from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


class ProductRepository:
    async def get_products_by_ids(
        self,
        db: AsyncSession,
        product_ids: list[int],
    ) -> list[Product]:
        if not product_ids:
            return []
        result = await db.execute(select(Product).where(Product.id.in_(product_ids)))
        return list(result.scalars().all())
