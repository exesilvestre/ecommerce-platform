from pydantic import BaseModel, ConfigDict, Field, conint
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
    shipping_address: str = Field(min_length=5)
    items: List[OrderItemCreateDTO] = Field(min_length=1)
    payment: PaymentInputDTO


class OrderCreateResponseDTO(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "order_id": 1,
                "warehouse_id": 2,
                "total_amount": "999.00",
                "status": "CONFIRMED",
                "payment_status": "SUCCESS",
            }
        }
    )

    order_id: int
    warehouse_id: int
    total_amount: Decimal = Field(json_schema_extra={"example": "999.00"})
    status: str
    payment_status: str
