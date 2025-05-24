"""
Varje konto identifieras med IBAN (internationellt bankkontonummer).
IBAN används som primärnyckel för att undvika dubbla ID:n och för att
säkerställa unika konton i databasen."""

from sqlalchemy import Column, Integer, ForeignKey, Float, String, CheckConstraint
from sqlalchemy.orm import relationship
from Pipeline.database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    iban = Column(String(34), primary_key=True)  # IBAN är unik identifierare
    customer_id = Column(Integer, ForeignKey("customers.id"))
    balance = Column(Float, default=0.0)
    currency_code = Column(String(3), default='SEK')

# Relation till kund
    customer = relationship("Customer", back_populates="accounts")

__table_args__ = (
        CheckConstraint('balance >= 0', name='check_balance_positive'),
    )