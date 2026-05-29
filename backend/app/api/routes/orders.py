import json
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.order_examples import ORDER_OPENAPI_EXAMPLES
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
        "Create an order from seed data. Requires an **Idempotency-Key** header (UUID). "
        "Pick an example from the dropdown, then use **Try it out**."
    ),
    responses={
        201: {"description": "Order created"},
        402: {"description": "Payment declined"},
        404: {"description": "Customer or product not found"},
        409: {"description": "Idempotency conflict or request in progress"},
        422: {"description": "No warehouse can fulfill the order or insufficient stock"},
    },
)
async def create_order(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
    payload: Annotated[OrderCreateDTO, Body(..., examples=ORDER_OPENAPI_EXAMPLES)],
):
    request_hash = hash_order_request(payload)
    idem = IdempotencyService()

    try:
        cached = await idem.resolve(db=db, key=idempotency_key, request_hash=request_hash)
    except IdempotencyConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except IdempotencyInProgressError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if cached:
        response.status_code = cached.response_status
        return json.loads(cached.response_body)

    await idem.acquire(db=db, key=idempotency_key, request_hash=request_hash)

    service = OrderService()
    try:
        result = await service.create_order(
            db=db,
            payload=payload,
            idempotency_key=idempotency_key,
            idempotency_request_hash=request_hash,
        )
    except PaymentFailedError:
        raise
    except Exception:
        await idem.abandon(db=db, key=idempotency_key)
        raise

    return OrderCreateResponseDTO(
        order_id=result.order.id,
        warehouse_id=result.order.warehouse_id,
        total_amount=result.order.total_amount,
        status=str(result.order.status.value),
        payment_status=str(result.payment.status.value),
    )
