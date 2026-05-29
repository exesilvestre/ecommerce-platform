from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.products import ProductDTO
from app.services.products import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductDTO])
async def list_products(db: AsyncSession = Depends(get_db)):
    service = ProductService()
    return await service.list_products(db=db)
