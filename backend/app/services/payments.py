from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from uuid import uuid4

from app.core.constants import ERR_PAYMENT_FAILED


class PaymentIntentStatus(str, Enum):
    REQUIRES_CONFIRMATION = "requires_confirmation"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True)
class PaymentIntent:
    id: str
    amount: Decimal
    currency: str
    description: str
    metadata: dict[str, str]
    status: PaymentIntentStatus


class PaymentFailedError(Exception):
    def __init__(self, message: str = ERR_PAYMENT_FAILED):
        super().__init__(message)


# In-memory store simulating Stripe's idempotent PaymentIntent API.
_intents_by_id: dict[str, PaymentIntent] = {}
_intent_id_by_idempotency_key: dict[str, str] = {}


class PaymentService:
    """Mock Stripe PaymentIntent API (create + confirm)."""

    async def create_payment_intent(
        self,
        *,
        amount: Decimal,
        currency: str,
        description: str,
        metadata: dict[str, str],
        idempotency_key: str,
    ) -> PaymentIntent:
        existing_id = _intent_id_by_idempotency_key.get(idempotency_key)
        if existing_id is not None:
            return _intents_by_id[existing_id]

        intent = PaymentIntent(
            id=f"pi_mock_{uuid4().hex}",
            amount=amount,
            currency=currency,
            description=description,
            metadata=dict(metadata),
            status=PaymentIntentStatus.REQUIRES_CONFIRMATION,
        )
        _intents_by_id[intent.id] = intent
        _intent_id_by_idempotency_key[idempotency_key] = intent.id
        return intent

    async def confirm_payment_intent(
        self,
        *,
        payment_intent_id: str,
        card_number: str,
        expiration_date: str,
    ) -> PaymentIntent:
        intent = _intents_by_id.get(payment_intent_id)
        if intent is None:
            raise PaymentFailedError("Payment intent not found.")

        if intent.status == PaymentIntentStatus.SUCCEEDED:
            return intent

        _ = expiration_date

        if card_number.endswith("0000"):
            failed = PaymentIntent(
                id=intent.id,
                amount=intent.amount,
                currency=intent.currency,
                description=intent.description,
                metadata=intent.metadata,
                status=PaymentIntentStatus.FAILED,
            )
            _intents_by_id[intent.id] = failed
            raise PaymentFailedError()

        confirmed = PaymentIntent(
            id=intent.id,
            amount=intent.amount,
            currency=intent.currency,
            description=intent.description,
            metadata=intent.metadata,
            status=PaymentIntentStatus.SUCCEEDED,
        )
        _intents_by_id[intent.id] = confirmed
        return confirmed
