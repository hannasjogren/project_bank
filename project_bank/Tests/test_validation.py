import pytest
import pandas as pd
from Pipeline.database import SessionLocal, Base, engine
from Models.transaction import Transaction
from Models.exchange_rate import ExchangeRate
from Services.transaction_service import create_transaction, validate_transaction
from Pipeline.validation import validate_iban_matches
from Models.customer import Customer


# Pytest-fixture: Skapar test-DB
@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    # Test-växelkurser
    session.add_all([
        ExchangeRate(currency_code="USD", rate_to_base=10.0),
        ExchangeRate(currency_code="EUR", rate_to_base=11.0),
        ExchangeRate(currency_code="SEK", rate_to_base=1.0),
    ])
    session.commit()

    yield session

    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)


# Databasbaserade tester
def test_transaction_currency_conversion(db):
    tx = Transaction(account_id=999, amount=100, currency_code='EUR')
    db.add(tx)
    with pytest.raises(Exception):
        db.commit()

def test_transaction_conversion(db):
    tx_data = {
        "account_id": "acc123",
        "amount": 100.0,
        "currency": "USD",
        "sender_country": "US",
        "receiver_country": "SE",
        "description": "Test USD transaction"
    }
    tx = create_transaction(tx_data, db)
    assert tx.amount_converted == 100.0 * 10.0
    assert tx.converted_currency == "SEK"

def test_unknown_currency(db):
    tx_data = {
        "account_id": "acc123",
        "amount": 50.0,
        "currency": "ABC",
        "sender_country": "US",
        "receiver_country": "SE",
    }
    with pytest.raises(ValueError) as e:
        create_transaction(tx_data, db)
    assert "Okänd valuta" in str(e.value)

def test_invalid_sender_country(db):
    tx_data = {
        "account_id": "acc123",
        "amount": 50.0,
        "currency": "SEK",
        "sender_country": "ZZ",
        "receiver_country": "SE",
    }
    with pytest.raises(ValueError) as e:
        create_transaction(tx_data, db)
    assert "Ogiltig sändarlandskod" in str(e.value)

def test_invalid_receiver_country(db):
    tx_data = {
        "account_id": "acc123",
        "amount": 50.0,
        "currency": "SEK",
        "sender_country": "SE",
        "receiver_country": "XX",
    }
    with pytest.raises(ValueError) as e:
        create_transaction(tx_data, db)
    assert "Ogiltig mottagarlandskod" in str(e.value)

# Valideringslogik (icke-DB)
def test_valid_transaction():
    tx = {
        "sender_account": "SE8930000000000000000001",
        "receiver_account": "SE8930000000000000000002",
        "sender_country": "Sweden",
        "receiver_country": "Sweden",
        "sender_municipality": "Stockholm",
        "receiver_municipality": "Gothenburg",
        "transaction_type": "outgoing",
        "notes": "Test transaction"
    }
    assert validate_transaction(tx) is True

def test_invalid_country():
    tx = {
        "sender_account": "SE8930000000000000000001",
        "receiver_account": "SE8930000000000000000002",
        "sender_country": "Neverland",
        "receiver_country": "Sweden",
        "sender_municipality": "Stockholm",
        "receiver_municipality": "Gothenburg",
        "transaction_type": "outgoing",
        "notes": "Bad country"
    }
    assert validate_transaction(tx) is False

# Pandas-baserade datatester
def test_validate_iban_matches():
    customers = pd.DataFrame({'IBAN': ['SE3550000000054910000003']})
    transactions = pd.DataFrame({'IBAN': ['SE3550000000054910000003', 'SE3550000000054919999999']})
    result = validate_iban_matches(transactions, customers)
    assert result['iban_valid'].tolist() == [True, False]

def test_iban_validation():
    transactions = pd.DataFrame({'iban_valid': [True, False, True]})
    assert all(transactions['iban_valid'].isin([True, False]))

def test_no_duplicate_bank_accounts():
    df = pd.read_csv('sebank_customers_with_accounts.csv')
    duplicates = df[df.duplicated(subset=['BankAccount'], keep=False)]
    assert duplicates.empty, f"Duplicate bank accounts found:\n{duplicates}"

def test_personnummer_length():
    df = pd.read_csv('sebank_customers_with_accounts.csv')
    assert df['Personnummer'].apply(lambda x: len(str(x)) == 13).all(), "Some personnummer entries do not have 13 characters"

# Modellbegränsning (Customer)
def test_customer_constraints():
    c = Customer(
        account_number="SE1234567890",
        name="Test Customer",
        country="Sweden",
        municipality="Stockholm"
    )
    assert len(c.account_number) >= 10