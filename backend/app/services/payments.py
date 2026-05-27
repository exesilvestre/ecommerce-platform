

class PaymentResult:
    def __init__(self, external_reference: str):
        self.external_reference = external_reference
    

class PaymentService:
    async def charge(self, card_number: str, expiration_date: str, amount: Decimal) -> PyamentResult:
       # Mock: always succeeds
        _ = (card_number, expiration_date, amount)

        return PaymentResult(external_reference="1234567890")
    
