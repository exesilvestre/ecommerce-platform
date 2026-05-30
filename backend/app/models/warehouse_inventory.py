from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer

from app.db.session import Base


class WarehouseInventory(Base):
    __tablename__ = "warehouse_inventory"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_warehouse_inventory_quantity_non_negative"),
    )

    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    quantity = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
