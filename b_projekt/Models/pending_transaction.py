#Hanterar pågående transaktioner som väntar på godkännande eller hantering,
# men som ännu inte är permanent registrerade eller flaggade.

from sqlalchemy import Column, String, Integer, DateTime, Float, CheckConstraint
from Pipeline.database import Base
from datetime import datetime

class PendingTransaction(Base):
    __tablename__ = "pending_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_account = Column(String, nullable=False)
    receiver_account = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)  # ISO 4217 valutakod
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        CheckConstraint("amount > 0", name="valid_amount"),  # Belopp måste vara positivt
        CheckConstraint("sender_account <> receiver_account", name="different_accounts"),  # Avsändare får inte skicka till sig själv
        CheckConstraint("length(currency) = 3", name="valid_currency_code"),  # ISO 4217 valutakod (3 tecken)
    )