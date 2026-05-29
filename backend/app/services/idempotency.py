
import hashlib
import json
from app.schemas.orders import OrderCreateDTO
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.idempotency_key import IdempotencyKey


def hash_order_request(payload: OrderCreateDTO) -> str:
    data = payload.model_dump(mode="json")
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class IdempotencyConflictError(Exception):
    pass

class IdempotencyService:
    async def get_cached(
        self,
        db: AsyncSession,
        key: str,
        request_hash: str,
    ) -> IdempotencyKey | None:
        row  = (
            await db.execute(
                select(IdempotencyKey)
                .where(IdempotencyKey.key == key)
            )
        ).scalar_one_or_none()

        if row is None:
            return None
        
        if row.request_hash != request_hash:
            raise IdempotencyConflictError("Idempotency-Key reused with different request body.")
        
        return row
    

    async def save(
        self,
        db: AsyncSession,
        key: str,
        request_hash: str,
        response_status: int,
        response_body: str,
    ) -> None:
        db.add(
            IdempotencyKey(
                key=key,
                request_hash=request_hash,
                response_status=response_status,
                response_body=response_body,
            )
        )
        
        try:
            await db.flush()
        except IntegrityError:
            raise IdempotencyConflictError("Idempotency-Key already exists with the same request body.")