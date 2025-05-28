#Hanterar validering av transaktioner och loggar resultatet i ValidationLog

from sqlalchemy.orm import Session
from Models.transaction import Transaction
from Models.ValidationLog import ValidationLog

def validate_transaction(session: Session, transaction: Transaction):
    is_valid = transaction.amount > 0
    validation_log = ValidationLog(
        transaction_id=transaction.id,
        is_valid=is_valid,
        validation_reason="OK" if is_valid else "Negativt belopp"
    )
    session.add(validation_log)
    session.commit()
    return is_valid