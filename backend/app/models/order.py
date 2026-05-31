from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.types import Numeric

from app.db.session import Base
from app.models.enums import OrderStatus


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    status = Column(
        Enum(OrderStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=OrderStatus.PENDING,
    )
    total_amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    shipping_address = Column(String, nullable=False)
    shipping_latitude = Column(Float, nullable=False)
    shipping_longitude = Column(Float, nullable=False)
