from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.session import Base


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"
    id = Column(Integer, primary_key=True)
    key = Column(String(255), unique=True, nullable=False)
    request_hash = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default="completed")
    response_status = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
