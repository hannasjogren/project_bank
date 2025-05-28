from sqlalchemy import Column, String
from Pipeline.database import Base

class Account(Base):
    __tablename__ = "accounts"

    iban = Column(String, primary_key=True)
    account_type = Column(String, nullable=False)