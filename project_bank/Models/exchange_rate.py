"""
Växelkurs mellan två valutor.
- Stöder godtyckliga valutapar (t.ex. USD → EUR, SEK → USD)
- Håller reda på när varje kurs senast uppdaterades."""

from sqlalchemy import Column, String, Float, DateTime, PrimaryKeyConstraint, CheckConstraint
from datetime import datetime, timezone
from Pipeline.database import Base

VALID_CURRENCIES = ['SEK', 'DKK', 'USD', 'EUR', 'JPY', 'ZMW', 'NOK', 'ZAR', 'RMB', 'GBP']

valid_currencies_sql = ",".join(f"'{c}'" for c in VALID_CURRENCIES)

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    from_currency = Column(String(3), nullable=False)
    to_currency = Column(String(3), nullable=False)
    rate = Column(Float, nullable=False)
    last_updated = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        PrimaryKeyConstraint('from_currency', 'to_currency', name="pk_currency_pair"),
        CheckConstraint(f"from_currency IN ({valid_currencies_sql})", name="check_valid_from_currency"),
        CheckConstraint(f"to_currency IN ({valid_currencies_sql})", name="check_valid_to_currency"),
    )
