from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


class ProductService:
    async def list_products(self, db: AsyncSession) -> list[Product]:
        result = await db.execute(select(Product).order_by(Product.id))
        return list(result.scalars().all())
