from sqlalchemy import Column, String, Float, DateTime, ForeignKey, CheckConstraint
from Pipeline.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True)  # Unik identifierare för transaktionen
    timestamp = Column(DateTime, nullable=False)  # Tidpunkt för transaktionen
    amount = Column(Float, nullable=False)  # Belopp
    currency = Column(String(3), nullable=False)  # Valuta (t.ex. SEK, EUR, USD)
    sender_account = Column(String(34), ForeignKey("accounts.iban"), nullable=False)  # Avsändarens konto
    receiver_account = Column(String(34), ForeignKey("accounts.iban"), nullable=False)  # Mottagarens konto
    sender_country = Column(String(50))  # Avsändarens land
    sender_municipality = Column(String(50))  # Avsändarens kommun
    receiver_country = Column(String(50))  # Mottagarens land
    receiver_municipality = Column(String(50))  # Mottagarens kommun
    transaction_type = Column(String, nullable=False)  # Typ av transaktion
    notes = Column(String)  # Extra information om transaktionen

    __table_args__ = (
        CheckConstraint("amount > 0", name="valid_amount"),  # Belopp måste vara positivt
        CheckConstraint("length(currency) = 3", name="valid_currency")  # Valutan måste vara 3 tecken (ISO-standard)
    )