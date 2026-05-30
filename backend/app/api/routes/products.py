from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_product_service
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.schemas.products import ProductDTO
from app.services.products import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductDTO])
@limiter.limit(settings.rate_limit_products)
async def list_products(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[ProductService, Depends(get_product_service)],
):
    return await service.list_products(db=db)
