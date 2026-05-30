import json
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_idempotency_service, get_order_service
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.schemas.orders import OrderCreateDTO, OrderCreateResponseDTO
from app.services.idempotency import (
    IdempotencyConflictError,
    IdempotencyInProgressError,
    IdempotencyService,
    hash_order_request,
)
from app.services.orders import OrderService
from app.services.payments import PaymentFailedError

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "",
    response_model=OrderCreateResponseDTO,
    status_code=201,
    summary="Create an order",
    description=(
        "Create an order from seed data. Requires an **Idempotency-Key** header (UUID).\n\n"
    ),
    responses={
        201: {"description": "Order created"},
        402: {"description": "Payment declined"},
        404: {"description": "Customer or product not found"},
        409: {"description": "Idempotency conflict or request in progress"},
        429: {"description": "Rate limit exceeded"},
        422: {
            "description": "Validation error (invalid Idempotency-Key or request body), "
            "or no warehouse / insufficient stock"
        },
    },
)
@limiter.limit(settings.rate_limit_orders)
async def create_order(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    idempotency_key: Annotated[UUID, Header(alias="Idempotency-Key")],
    payload: Annotated[OrderCreateDTO, Body()],
    idem: Annotated[IdempotencyService, Depends(get_idempotency_service)],
    service: Annotated[OrderService, Depends(get_order_service)],
):
    key = str(idempotency_key)
    request_hash = hash_order_request(payload)

    try:
        cached = await idem.resolve(db=db, key=key, request_hash=request_hash)
    except IdempotencyConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except IdempotencyInProgressError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if cached:
        response.status_code = cached.response_status
        return json.loads(cached.response_body)

    await idem.acquire(db=db, key=key, request_hash=request_hash)

    try:
        result = await service.create_order(
            db=db,
            payload=payload,
            idempotency_key=key,
            idempotency_request_hash=request_hash,
        )
    except PaymentFailedError:
        raise
    except Exception:
        await idem.abandon(db=db, key=key)
        raise

    return OrderCreateResponseDTO(
        order_id=result.order.id,
        warehouse_id=result.order.warehouse_id,
        total_amount=result.order.total_amount,
        status=str(result.order.status.value),
        payment_status=str(result.payment.status.value),
    )
