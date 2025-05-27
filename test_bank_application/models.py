import re
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.orm import relationship, declarative_base, validates
from datetime import datetime

Base = declarative_base()

# --------------------------------------------- CUSTOMER --------------------------------------------- #
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    customer = Column(String, nullable=False)
    address = Column(String)
    phone = Column(String)
    personnummer = Column(String, unique=True, nullable=False)
    iban = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime)
    age = Column(Integer, nullable=False)

    accounts = relationship("BankAccount")

    @validates('phone')
    def validate_phone(self, key, phone):
        pattern = re.compile(r"^(\+46|0)[- ]?(\d{8,9})$")
        if not pattern.match(phone):
            raise ValueError(f"Invalid Swedish phone number format: {phone}")
        return phone


def calculate_age_from_ssn(ssn: str) -> int:
    ssn = ssn.replace('-', '').replace('+', '')
    if len(ssn) == 12:
        birth_str = ssn[:8]
        birth_date = datetime.strptime(birth_str, '%Y%m%d')
    elif len(ssn) == 10:
        birth_str = ssn[:6]
        year = int(birth_str[:2])
        current_year = datetime.now().year % 100
        if year > current_year:
            year_prefix = 1900
        else:
            year_prefix = 2000
        full_year = year_prefix + year
        birth_str_full = str(full_year) + birth_str[2:]
        birth_date = datetime.strptime(birth_str_full, '%Y%m%d')
    else:
        raise ValueError("Ogiltigt personnummerformat")

    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

__table_args__ = (
    CheckConstraint('age >= 18 AND age <= 80', name='check_age_range'),
    ) #är en kolumn i databasen med CheckConstraint som ser till att åldern alltid är mellan 18 och 80

@classmethod
def from_csv_row(cls, row): #from_csv_row skapar en Customer-instans från CSV-data och fyller i age automatiskt
    name = row[0]
    adress = row[1]
    phone = row[2]
    ssn = row[3]
    iban = row[4]
    created_at = datetime.now()

    age = calculate_age_from_ssn(ssn) #beräknar ålder från personnummer i format YYMMDD-XXXX
    return cls(
        name=name,
        adress=adress,
        phone=phone,
        ssn=ssn,
        iban=iban,
        created_at=created_at,
        age=age
        )

# --------------------------------------------- ACCOUNT --------------------------------------------- #
class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
# --------------------------------------------- TRANSACTION --------------------------------------------- #
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, nullable=False, unique=True)
    timestamp = Column(DateTime, nullable=False)
    amount = Column(DECIMAL, nullable=False)
    currency = Column(String(3), nullable=False)
    sender_country = Column(String)
    receiver_country = Column(String)
    sender_municipality = Column(String)
    receiver_municipality = Column(String)
    transaction_type = Column(String, nullable=False)
    notes = Column(String)
    rate = Column(DECIMAL)
    in_sek = Column(String)

    sender_account = Column(Integer, ForeignKey("bank_accounts.id"))
    receiver_account = Column(Integer, ForeignKey("bank_accounts.id"))

