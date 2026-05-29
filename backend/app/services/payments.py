from decimal import Decimal

from app.core.constants import ERR_PAYMENT_FAILED


class PaymentFailedError(Exception):
    def __init__(self, message: str = ERR_PAYMENT_FAILED):
        super().__init__(message)


class PaymentResult:
    def __init__(self, external_reference: str):
        self.external_reference = external_reference


class PaymentService:
    async def charge(
        self,
        card_number: str,
        expiration_date: str,
        amount: Decimal,
    ) -> PaymentResult:
        _ = (expiration_date, amount)

        if card_number.endswith("0000"):
            raise PaymentFailedError()

        return PaymentResult(external_reference="1234567890")
