from sqlalchemy import Column, String, func
from sqlalchemy.orm import Session
from Models.transaction import Transaction
from Pipeline.database import Base


class Blacklist(Base):
    __tablename__ = 'blacklist'
    iban = Column(String(34), primary_key=True)


def is_amount_suspicious(amount: float) -> bool:
    """Flagga stora eller negativa belopp"""
    return amount > 1_000_000 or amount < 0


def detect_fraud(transaction: Transaction, blacklist_ibans: set) -> tuple[bool, str | None]:
    if transaction.sender_iban in blacklist_ibans:
        return True, "Sender is blacklisted"

    if transaction.receiver_iban in blacklist_ibans:
        return True, "Receiver is blacklisted"

    if is_amount_suspicious(transaction.amount):
        return True, "Suspicious amount"

    # Lägg till fler regler här efter behov

    return False, None


def detect_looping_transactions(history: list) -> bool:
    """Returnerar True om samma transaktion återkommer onormalt ofta."""
    return len(set(history)) < len(history)


def get_suspicious_transactions(db: Session) -> list[Transaction]:
    """
    Hämtar misstänkta transaktioner från DB baserat på regler:
    - Stora belopp
    - Många transaktioner till samma konto
    """
    large_tx = db.query(Transaction).filter(Transaction.amount > 100000).all()

    frequent_targets = (
        db.query(Transaction.receiver_account, func.count(Transaction.id).label("count"))
        .group_by(Transaction.receiver_account)
        .having(func.count(Transaction.id) > 100)
        .all()
    )

    suspicious = set(large_tx)
    for target, _ in frequent_targets:
        txs = db.query(Transaction).filter(Transaction.receiver_account == target).all()
        suspicious.update(txs)

    return list(suspicious)
