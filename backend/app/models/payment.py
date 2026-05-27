from app.db.session import Base
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, String, Enum
from datetime import datetime
from app.models.enums import PaymentStatus
from sqlalchemy.types import Numeric


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    external_reference = Column(String, nullable=True)    
    credit_card_number = Column(String, nullable=False)
    credit_card_expiration_date = Column(String, nullable=False)
