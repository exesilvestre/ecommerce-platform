from app.db.session import Base
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, String, Enum
from datetime import datetime
from app.models.enums import OrderStatus
from sqlalchemy.types import Numeric



class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    total_amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    shipping_address = Column(String, nullable=False)
    shipping_latitude = Column(Float, nullable=False)
    shipping_longitude = Column(Float, nullable=False)
