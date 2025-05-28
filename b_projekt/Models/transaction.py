from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from Pipeline.database import Base
from datetime import datetime

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    amount = Column(DECIMAL(12, 2), nullable=False)  # Precision för korrekt belopp
    currency = Column(String, nullable=False)
    sender_account = Column(String, ForeignKey("accounts.iban"), nullable=False)
    receiver_account = Column(String, ForeignKey("accounts.iban"), nullable=False)
    sender_country = Column(String, nullable=False)
    receiver_country = Column(String, nullable=False)
    description = Column(String, default="Unknown")  # Förhindrar NULL