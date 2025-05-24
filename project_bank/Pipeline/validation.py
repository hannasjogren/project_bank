#Validering och logg till DB
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func
from Models import ValidationLog
from Models.transaction import Transaction
from Pipeline.logging_setup import setup_logger

logger = setup_logger()

def validate_iban_matches(transactions: pd.DataFrame, customers: pd.DataFrame, session: Session):
    valid_ibans = set(customers['IBAN'])
    transactions['iban_valid'] = transactions['IBAN'].isin(valid_ibans)

    for _, row in transactions.iterrows():
        valid = row['iban_valid']
        logger.info(f"Transaction {row['IBAN']} validation: {valid}")
        log = ValidationLog(transaction_iban=row['IBAN'], is_valid=valid)
        session.add(log)

    session.commit()  # Spara alla loggar i DB
    return transactions


#Funktion för bedrägerihantering

def is_fraudulent_transaction(tx):
    if tx['amount'] > 100000:
        return True
    if tx['amount'] < 0:
        return True
    return False

def detect_fraud(transaction, blacklist_ibans):
    if transaction.sender_iban in blacklist_ibans:
        return True, "Sender is blacklisted"

    if transaction.receiver_iban in blacklist_ibans:
        return True, "Receiver is blacklisted"

    if transaction.amount > 100000:  # exempel på högt belopp
        return True, "Amount exceeds threshold"
    
    return False, None

def detect_suspicious_amount(amount):
    return amount > 1_000_000

def detect_looping_transaction(history):
    return len(set(history)) < len(history)

def get_suspicious_transactions(db: Session):
    large_tx = db.query(Transaction).filter(Transaction.amount > 100000).all()
    frequent_targets = (
        db.query(Transaction.target_account_id, func.count(Transaction.id).label("count"))
        .group_by(Transaction.target_account_id)
        .having(func.count(Transaction.id) > 100)
        .all()
    )
    suspicious = set(large_tx)
    for target, _ in frequent_targets:
        txs = db.query(Transaction).filter(Transaction.target_account_id == target).all()
        suspicious.update(txs)
    return list(suspicious)
