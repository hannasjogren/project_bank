from sqlalchemy import Column, Integer, String, Float, DateTime
from Pipeline.database import Base
from datetime import datetime

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_from = Column(String, nullable=False)
    currency_to = Column(String, nullable=False)
    rate = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.now)