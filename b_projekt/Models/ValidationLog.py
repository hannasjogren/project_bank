from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, CheckConstraint
from Pipeline.database import Base
from datetime import datetime

class ValidationLog(Base):
    __tablename__ = "validation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    is_valid = Column(Boolean, nullable=False)
    validation_reason = Column(String, nullable=False)

    __table_args__ = (
        CheckConstraint("is_valid IN (0, 1)", name="valid_boolean"),  # Säkerställer att `is_valid` är True eller False
        CheckConstraint("length(validation_reason) > 5", name="valid_reason_length"),  # Krav på minst 5 tecken i `validation_reason`
    )