#Automatiserad pipeline med prefect
#Ändra LOG_FILE till er egna filväg
import pandas as pd
import re
import os
import logging
from decimal import Decimal
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from prefect import task, flow
from Pipeline.database import SessionLocal, Base, engine
from Models.customer import Customer
from Models.account import Account
from Models.transaction import Transaction
from Models.pending_transaction import PendingTransaction  # Importerar väntelistan

# Loggning
LOG_FILE = r"C:\Users\hanna\PycharmProjects\b_projekt\Logs\pipeline.log"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(stream_handler)


# Kontroll av databasanslutning
@task
def check_database():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Databasanslutningen är korrekt!")
    except Exception as db_error:
        raise Exception(f"Databasanslutningen misslyckades: {db_error}")


# Se till att alla tabeller skapas automatiskt
Base.metadata.create_all(bind=engine)

# Filvägar
DATA_DIR = r"C:\Users\hanna\PycharmProjects\b_projekt\Data"
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.csv")
ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.csv")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.csv")


@task
def import_customers(session):
    try:
        customers_df = pd.read_csv(CUSTOMERS_FILE)
        customers_df.dropna(subset=["Phone"], inplace=True)
        customers_df.drop_duplicates(subset=["Phone"], inplace=True)

        for _, row in customers_df.iterrows():
            existing_customer = session.query(Customer).filter_by(personnummer=row["Personnummer"]).first()
            if not existing_customer:
                customer = Customer(
                    personnummer=row["Personnummer"],
                    customer=row["Customer"],
                    address=row["Address"],
                    phone=row["Phone"]
                )
                session.add(customer)

        session.commit()
        logger.info(f"Importerade {session.query(Customer).count()} kunder till databasen")
    except SQLAlchemyError as error:
        session.rollback()
        logger.error(f"Fel vid import av kunder: {error}")


@task
def import_accounts(session):
    try:
        accounts_df = pd.read_csv(ACCOUNTS_FILE)
        accounts_df.drop_duplicates(subset=["iban"], inplace=True)

        for _, row in accounts_df.iterrows():
            existing_account = session.query(Account).filter_by(iban=row["iban"]).first()
            if not existing_account:
                account = Account(
                    personnummer=row["Personnummer"],
                    iban=row["iban"]
                )
                session.add(account)

        session.commit()
        logger.info(f"Importerade {session.query(Account).count()} konton till databasen")
    except SQLAlchemyError as error:
        session.rollback()
        logger.error(f"Fel vid import av konton: {error}")


@task
def import_transactions(session):
    try:
        transactions_df = pd.read_csv(TRANSACTIONS_FILE)
        transactions_df["amount"] = transactions_df["amount"].apply(
            lambda x: Decimal(str(x)) if pd.notna(x) else Decimal('0'))
        transactions_df.dropna(subset=["sender_account", "receiver_account", "amount"], inplace=True)

        pending_count = 0

        for _, row in transactions_df.iterrows():
            sender_country = str(row["sender_country"]).strip() if pd.notna(row["sender_country"]) else "Unknown"
            receiver_country = str(row["receiver_country"]).strip() if pd.notna(row["receiver_country"]) else "Unknown"
            notes = str(row["notes"]).strip() if pd.notna(row["notes"]) else "Unknown"

            sender_country = re.sub(r"[^\w\s]", "", sender_country)
            receiver_country = re.sub(r"[^\w\s]", "", receiver_country)

            existing_sender = session.query(Account).filter_by(iban=row["sender_account"]).first()
            existing_receiver = session.query(Account).filter_by(iban=row["receiver_account"]).first()

            if not existing_sender or not existing_receiver:
                logger.warning(
                    f"Sparar transaktion i PendingTransaction, saknat konto: {row['sender_account']} → {row['receiver_account']}")
                pending_transaction = PendingTransaction(
                    sender_account=row["sender_account"],
                    receiver_account=row["receiver_account"],
                    amount=row["amount"],
                    currency=row["currency"]
                )
                session.add(pending_transaction)
                pending_count += 1
                continue

            transaction = Transaction(
                transaction_id=row["transaction_id"],
                timestamp=pd.to_datetime(row["timestamp"]),
                amount=row["amount"],
                currency=row["currency"],
                sender_account=row["sender_account"],
                receiver_account=row["receiver_account"],
                sender_country=sender_country,
                sender_municipality=row.get("sender_municipality", "Unknown"),
                receiver_country=receiver_country,
                receiver_municipality=row.get("receiver_municipality", "Unknown"),
                transaction_type=row["transaction_type"],
                notes=notes
            )
            session.add(transaction)

        session.commit()
        logger.info(f"Importerade {session.query(Transaction).count()} transaktioner")
        logger.info(f"Sparade {pending_count} transaktioner i väntelistan")
    except SQLAlchemyError as error:
        session.rollback()
        logger.error(f"Fel vid import av transaktioner: {error}")


@flow(name="Data Import Pipeline")
def main_flow():
    check_database()

    # Använd en enda session för hela flödet
    with SessionLocal() as session:
        import_customers(session)
        import_accounts(session)
        import_transactions(session)

    logger.info("Pipeline genomförd! Alla data har importerats korrekt.")


if __name__ == "__main__":
    main_flow()