from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.types import Numeric

from app.db.session import Base
from app.models.enums import PaymentStatus


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(
        Enum(PaymentStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=PaymentStatus.PENDING,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    payment_intent_id = Column(String, nullable=True, unique=True)
    external_reference = Column(String, nullable=True)
