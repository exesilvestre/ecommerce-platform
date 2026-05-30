from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_product_service
from app.db.session import get_db
from app.schemas.products import ProductDTO
from app.services.products import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductDTO])
async def list_products(
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[ProductService, Depends(get_product_service)],
):
    return await service.list_products(db=db)
