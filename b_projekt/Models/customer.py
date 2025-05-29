from sqlalchemy import Column, String, CheckConstraint
from Pipeline.database import Base

class Customer(Base):
    __tablename__ = "customers"

    personnummer = Column(String(12), unique=True, primary_key=True)
    customer = Column(String, nullable=False)
    address = Column(String)
    phone = Column(String, unique=True)

    __table_args__ = (
        CheckConstraint("length(personnummer) >= 10 AND length(personnummer) <= 12", name="valid_personnummer"),
        CheckConstraint("length(phone) >= 7", name="valid_phone_number")
    )