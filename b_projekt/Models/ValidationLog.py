from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from Pipeline.database import Base
from datetime import datetime

class ValidationLog(Base):
    __tablename__ = "validation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    is_valid = Column(Boolean, nullable=False)
    validation_reason = Column(String, nullable=False)