from sqlalchemy import Column, Integer, String, ForeignKey
from Pipeline.database import Base

class Blacklist(Base):
    __tablename__ = "blacklist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_iban = Column(String, ForeignKey("accounts.iban"), unique=True, nullable=False)
    reason = Column(String, nullable=False)