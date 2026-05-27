from app.db.session import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime

class WarehouseInventory(Base):
    __tablename__ = "warehouse_inventory"
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    quantity = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
