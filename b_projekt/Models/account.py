from sqlalchemy import Column, String, ForeignKey, CheckConstraint, UniqueConstraint
from Pipeline.database import Base

class Account(Base):
    __tablename__ = "accounts"

    personnummer = Column(String(12), ForeignKey("customers.personnummer"), primary_key=True)
    iban = Column(String(34), unique=True, primary_key=True, nullable=False)

    __table_args__ = (
        CheckConstraint("length(personnummer) >= 10 AND length(personnummer) <= 12", name="valid_personnummer"),
        CheckConstraint("length(iban) >= 15 AND length(iban) <= 34", name="valid_iban"),
        UniqueConstraint("iban", name="unique_iban")  # Lägger till explicit unik constraint
    )

