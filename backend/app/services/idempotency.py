import hashlib
import json

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.idempotency_key import IdempotencyKey
from app.schemas.orders import OrderCreateDTO


def hash_order_request(payload: OrderCreateDTO) -> str:
    data = payload.model_dump(mode="json")
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class IdempotencyConflictError(Exception):
    pass


class IdempotencyInProgressError(Exception):
    pass


class IdempotencyService:
    async def resolve(
        self,
        db: AsyncSession,
        key: str,
        request_hash: str,
    ) -> IdempotencyKey | None:
        row = (
            await db.execute(select(IdempotencyKey).where(IdempotencyKey.key == key))
        ).scalar_one_or_none()

        if row is None:
            return None

        if row.request_hash != request_hash:
            raise IdempotencyConflictError(
                "Idempotency-Key reused with different request body."
            )

        if row.status == "processing":
            raise IdempotencyInProgressError("Request already in progress.")

        return row

    async def acquire(
        self,
        db: AsyncSession,
        key: str,
        request_hash: str,
    ) -> None:
        db.add(
            IdempotencyKey(
                key=key,
                request_hash=request_hash,
                status="processing",
                response_status=None,
                response_body=None,
            )
        )
        try:
            await db.flush()
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise IdempotencyConflictError("Idempotency-Key already exists.") from None

    async def complete(
        self,
        db: AsyncSession,
        key: str,
        response_status: int,
        response_body: str,
    ) -> None:
        row = (
            await db.execute(
                select(IdempotencyKey)
                .where(IdempotencyKey.key == key)
                .with_for_update()
            )
        ).scalar_one()
        row.status = "completed"
        row.response_status = response_status
        row.response_body = response_body
        await db.flush()
        await db.commit()

    async def abandon(self, db: AsyncSession, key: str) -> None:
        await db.execute(
            delete(IdempotencyKey).where(
                IdempotencyKey.key == key,
                IdempotencyKey.status == "processing",
            )
        )
        await db.commit()
