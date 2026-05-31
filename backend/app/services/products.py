from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.order_errors import ProductsNotFoundError
from app.models.product import Product
from app.repositories.product_repository import ProductRepository


class ProductService:
    def __init__(
        self, product_repository: ProductRepository | None = None
    ) -> None:
        self.product_repository = product_repository or ProductRepository()

    async def list_products(self, db: AsyncSession) -> list[Product]:
        result = await db.execute(select(Product).order_by(Product.id))
        return list(result.scalars().all())

    async def get_products_by_ids(
        self,
        db: AsyncSession,
        product_ids: list[int],
    ) -> dict[int, Product]:
        rows = await self.product_repository.get_products_by_ids(
            db=db, product_ids=product_ids
        )
        products_by_id = {product.id: product for product in rows}
        missing_ids = sorted(set(product_ids) - set(products_by_id.keys()))
        if missing_ids:
            raise ProductsNotFoundError(missing_ids)
        return products_by_id
