from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone
from Pipeline.database import Base

class ValidationLog(Base):
    __tablename__ = "validation_logs"

    id = Column(Integer, primary_key=True, index=True)
    transaction_iban = Column(String, nullable=False)
    is_valid = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
