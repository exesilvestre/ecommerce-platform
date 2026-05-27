from decimal import Decimal
from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator


DEFAULT_CUSTOMER_EMAIL = "jane.homebuyer@example.com"


class SeedCustomerSchema(BaseModel):
    name: str = Field(min_length=1)
    email: str = Field(min_length=3)
    phone: str = Field(min_length=3)


class SeedProductSchema(BaseModel):
    ref: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str | None = None
    price: Decimal = Field(gt=0)


class SeedInventoryItemSchema(BaseModel):
    product_ref: str = Field(min_length=1)
    quantity: int = Field(gt=0)


class SeedWarehouseSchema(BaseModel):
    name: str = Field(min_length=1)
    address: str = Field(min_length=5)
    latitude: float
    longitude: float
    inventory: list[SeedInventoryItemSchema] = Field(min_length=1)

    @field_validator("address")
    @classmethod
    def address_must_end_with_usa(cls, value: str) -> str:
        if not value.strip().upper().endswith("USA"):
            raise ValueError("warehouse address must end with USA")
        return value

    @field_validator("latitude")
    @classmethod
    def latitude_in_usa_range(cls, value: float) -> float:
        if not 24.0 <= value <= 50.0:
            raise ValueError("latitude must be within continental USA range (24-50)")
        return value

    @field_validator("longitude")
    @classmethod
    def longitude_in_usa_range(cls, value: float) -> float:
        if not -125.0 <= value <= -66.0:
            raise ValueError("longitude must be within continental USA range (-125 to -66)")
        return value


class SeedDataSchema(BaseModel):
    customer: SeedCustomerSchema
    products: list[SeedProductSchema] = Field(min_length=1)
    warehouses: list[SeedWarehouseSchema] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_product_refs(self) -> Self:
        refs = [product.ref for product in self.products]
        if len(refs) != len(set(refs)):
            raise ValueError("product refs must be unique")

        known_refs = set(refs)
        for warehouse in self.warehouses:
            for item in warehouse.inventory:
                if item.product_ref not in known_refs:
                    raise ValueError(
                        f"unknown product_ref '{item.product_ref}' "
                        f"in warehouse '{warehouse.name}'"
                    )
        return self
