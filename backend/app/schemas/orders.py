from pydantic import BaseModel, Field, conint
from typing import List
from decimal import Decimal

class OrderItemCreateDTO(BaseModel):
    product_id: int
    quantity: conint(gt=0)


class PaymentInputDTO(BaseModel):
    credit_card_number: str = Field(min_length=16, max_length=16)
    credit_card_expiration_date: str = Field(description="Format: MMYY", min_length=4, max_length=4)


class OrderCreateDTO(BaseModel):
    customer_id: int
    shipping_address: str =Field(min_length=5)
    items: List[OrderItemCreateDTO] = Field(min_length=1)
    payment: PaymentInputDTO


class OrderCreateResponseDTO(BaseModel):
    order_id: int
    warehouse_id: int
    total_amount: Decimal
    status: str
    payment_status: str
