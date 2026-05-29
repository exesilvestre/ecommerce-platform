import enum


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    AWAITING_PAYMENT = "awaiting_payment"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
