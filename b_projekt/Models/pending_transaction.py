from sqlalchemy import Column, String, Integer, DateTime, Float
from Pipeline.database import Base
from datetime import datetime

class PendingTransaction(Base):
    __tablename__ = "pending_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_account = Column(String, nullable=False)
    receiver_account = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.now)