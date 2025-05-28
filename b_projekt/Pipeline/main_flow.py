#Manuell pipeline
#Ändra LOG_FILE till er egna filväg
#Ändra CSV path till er egna
import pandas as pd
import re
from decimal import Decimal
import logging
from Pipeline.database import SessionLocal, Base, engine
from Models.customer import Customer
from Models.account import Account
from Models.transaction import Transaction
from Models.pending_transaction import PendingTransaction  # Importerar väntelistan

# Loggning
LOG_FILE = r"C:\Users\hanna\PycharmProjects\b_projekt\Logs\pipeline.log"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(stream_handler)

# Se till att alla tabeller skapas automatiskt
Base.metadata.create_all(bind=engine)

# Filvägar
# Ändra till er egna filväg
CUSTOMERS_CSV = r"C:\Users\hanna\PycharmProjects\b_projekt\Data\customers.csv"
ACCOUNTS_CSV = r"C:\Users\hanna\PycharmProjects\b_projekt\Data\accounts.csv"
TRANSACTIONS_CSV = r"C:\Users\hanna\PycharmProjects\b_projekt\Data\transactions.csv"

def import_customers():
    session = SessionLocal()
    customers_df = pd.read_csv(CUSTOMERS_CSV)

    customers_df = customers_df.drop_duplicates(subset=["Phone"])

    for _, row in customers_df.iterrows():
        existing_customer = session.query(Customer).filter_by(phone=row["Phone"]).first()
        if not existing_customer:
            customer = Customer(
                customer=row["Customer"],
                address=row["Address"],
                phone=row["Phone"],
                personnummer=row["Personnummer"]
            )
            session.add(customer)

    session.commit()
    logger.info(f"Importerade {session.query(Customer).count()} kunder till databasen")
    session.close()

def import_accounts():
    session = SessionLocal()
    accounts_df = pd.read_csv(ACCOUNTS_CSV)

    accounts_df = accounts_df.drop_duplicates(subset=["BankAccount"])

    for _, row in accounts_df.iterrows():
        existing_account = session.query(Account).filter_by(iban=row["BankAccount"]).first()
        if not existing_account:
            account = Account(
                iban=row["BankAccount"],
                account_type="Standard"
            )
            session.add(account)

    session.commit()
    logger.info(f"Importerade {session.query(Account).count()} konton till databasen")
    session.close()

def import_transactions():
    session = SessionLocal()

    Base.metadata.create_all(bind=engine)

    transactions_df = pd.read_csv(TRANSACTIONS_CSV)

    transactions_df["amount"] = transactions_df["amount"].apply(lambda x: Decimal(str(x)) if pd.notna(x) else Decimal('0'))

    pending_count = 0

    for _, row in transactions_df.iterrows():
        sender_country = str(row["sender_country"]).strip() if pd.notna(row["sender_country"]) else "Unknown"
        receiver_country = str(row["receiver_country"]).strip() if pd.notna(row["receiver_country"]) else "Unknown"
        description = str(row["notes"]).strip() if pd.notna(row["notes"]) else "Unknown"

        sender_country = re.sub(r"[^\w\s]", "", sender_country)
        receiver_country = re.sub(r"[^\w\s]", "", receiver_country)

        existing_sender = session.query(Account).filter_by(iban=row["sender_account"]).first()
        existing_receiver = session.query(Account).filter_by(iban=row["receiver_account"]).first()

        if not existing_sender or not existing_receiver:
            logger.warning(f"Sparar transaktion i PendingTransaction, saknat konto: {row['sender_account']} → {row['receiver_account']}")
            pending_transaction = PendingTransaction(
                sender_account=row["sender_account"],
                receiver_account=row["receiver_account"],
                amount=row["amount"],
                currency=row["currency"]
            )
            session.add(pending_transaction)
            pending_count += 1
            continue

        logger.info(f"Insätter transaktion med belopp: {row['amount']} ({type(row['amount'])})")

        transaction = Transaction(
            sender_account=row["sender_account"],
            receiver_account=row["receiver_account"],
            amount=row["amount"],
            currency=row["currency"],
            timestamp=pd.to_datetime(row["timestamp"]),
            sender_country=sender_country,
            receiver_country=receiver_country,
            description=description
        )
        session.add(transaction)

    logger.info(f"Antal transaktioner i session innan commit: {session.query(Transaction).count()}")
    session.commit()
    logger.info(f"Importerade {session.query(Transaction).count()} transaktioner")
    logger.info(f"Sparade {pending_count} transaktioner i väntelistan")
    session.close()

if __name__ == "__main__":
    import_customers()
    import_accounts()
    import_transactions()