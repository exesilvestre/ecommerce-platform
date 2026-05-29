from fastapi import APIRouter

from app.schemas.orders import OrderCreateResponseDTO
from app.services.orders import OrderService
from app.schemas.orders import OrderCreateDTO
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("", response_model=OrderCreateResponseDTO)
async def create_order(payload: OrderCreateDTO, db: AsyncSession = Depends(get_db)):
    service = OrderService()
    result = await service.create_order(db=db, payload=payload)
    return OrderCreateResponseDTO(
        order_id=result.order.id,
        warehouse_id=result.order.warehouse_id,
        total_amount=result.order.total_amount,
        status=str(result.order.status.value),
        payment_status=str(result.payment.status.value),
    )



