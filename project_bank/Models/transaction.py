#SQLAlchemy-modeller med CHECK
from sqlalchemy import Column, Integer, Float, ForeignKey, String, DateTime, CheckConstraint
from datetime import datetime, timezone
from Pipeline.database import Base

# Lista över giltiga ISO 3166-1 alpha-2 koder
VALID_COUNTRY_CODES = [
    "SE", "US", "DE", "FR", "GB", "CN", "JP", "NO", "FI", "DK"
]

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    amount_converted = Column(Float, nullable=True)
    converted_currency = Column(String(3), nullable=True)
    sender_country = Column(String(2), nullable=False)
    receiver_country = Column(String(2), nullable=False)
    description = Column(String, nullable=True)
    
__table_args__ = (
        CheckConstraint(f"sender_country IN ({', '.join(['\''+c+'\'' for c in VALID_COUNTRY_CODES])})",
                        name="check_sender_country_valid"),
        CheckConstraint(f"receiver_country IN ({', '.join(['\''+c+'\'' for c in VALID_COUNTRY_CODES])})",
                        name="check_receiver_country_valid"),
    )
