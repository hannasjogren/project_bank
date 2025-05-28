from sqlalchemy import Column, Integer, String
from Pipeline.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    personnummer = Column(String, unique=True, nullable=False)