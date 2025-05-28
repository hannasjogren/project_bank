#---fetch_transactions(session)---
# Hämtar alla transaktioner från databasen.

#---save_transaction(session, transaction)---
# Sparar en transaktion, men i main_flow.py görs detta redan i import_transactions().

#---get_transactions_by_account(session, iban)---
# Hämtar transaktioner för ett specifikt konto,
# vilket kan vara användbart vid filtrering av transaktionshistorik.


from sqlalchemy.orm import Session
from Models.transaction import Transaction
from Models.account import Account

def fetch_transactions(session: Session):
    return session.query(Transaction).all()

def save_transaction(session: Session, transaction: Transaction):
    sender_account = session.query(Account).filter_by(iban=transaction.sender_account).first()
    receiver_account = session.query(Account).filter_by(iban=transaction.receiver_account).first()

    if not sender_account or not receiver_account:
        raise ValueError("Ogiltigt konto! En eller båda IBAN saknas.")

    session.add(transaction)
    session.commit()

def get_transactions_by_account(session: Session, iban: str):
    return session.query(Transaction).filter(
        (Transaction.sender_account == iban) | (Transaction.receiver_account == iban)
    ).all()