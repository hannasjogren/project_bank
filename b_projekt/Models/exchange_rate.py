from sqlalchemy import Column, Integer, String, Float, DateTime, CheckConstraint
from Pipeline.database import Base
from datetime import datetime

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_from = Column(String, nullable=False)
    currency_to = Column(String, nullable=False)
    rate = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        CheckConstraint("rate > 0", name="valid_rate"),  # Valutakurs måste vara positiv
        CheckConstraint("currency_from <> currency_to", name="different_currencies"),  # Valutorna måste vara olika
        CheckConstraint("length(currency_from) = 3 AND length(currency_to) = 3", name="valid_currency_code")  # ISO 4217-valutakod
    )
