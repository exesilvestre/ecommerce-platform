import json
from fastapi import APIRouter, Header, Response

from app.schemas.orders import OrderCreateResponseDTO
from app.services.orders import OrderService
from app.schemas.orders import OrderCreateDTO
from app.db.session import get_db
from app.services.idempotency import IdempotencyConflictError, IdempotencyService
from app.services.idempotency import hash_order_request
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("", response_model=OrderCreateResponseDTO, status_code=201)
async def create_order(
    payload: OrderCreateDTO, 
    response: Response,
    db: AsyncSession = Depends(get_db),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
):
    request_hash = hash_order_request(payload)
    idem = IdempotencyService()

    try:
        cached = await idem.get_cached(db=db, key=idempotency_key, request_hash=request_hash)
    except IdempotencyConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    
    if cached:
        response.status_code = cached.response_status
        return json.loads(cached.response_body)
    
    service = OrderService()
    result = await service.create_order(
        db=db, 
        payload=payload, 
        idempotency_key=idempotency_key, 
        idempotency_request_hash=request_hash,
    )
    
    return OrderCreateResponseDTO(
        order_id=result.order.id,
        warehouse_id=result.order.warehouse_id,
        total_amount=result.order.total_amount,
        status=str(result.order.status.value),
        payment_status=str(result.payment.status.value),
    )



