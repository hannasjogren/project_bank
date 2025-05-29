from sqlalchemy import Column, String, DECIMAL
from Pipeline.database import Base

class Blacklist(Base):
    __tablename__ = "blacklist"

    account_iban = Column(String(34), primary_key=True)  # Unikt IBAN
    reason = Column(String, nullable=False)  # Orsak till svartlistning
    amount = Column(DECIMAL(12, 2), nullable=False)  # Hanterar decimaler korrekt
    sender_country = Column(String)
    receiver_country = Column(String)