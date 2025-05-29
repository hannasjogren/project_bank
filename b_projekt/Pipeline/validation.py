import json
#import great_expectations as ge
from Pipeline.database import SessionLocal
from Models.transaction import Transaction
from Models.account import Account

CHECKPOINT_DIR = "checkpoints"
ALLOWED_CURRENCIES = {"SEK", "USD", "EUR", "DKK", "JPY", "ZMW", "NOK", "ZAR", "RMB", "GBP"}


def validate_transactions():
    session = SessionLocal()
    transactions = session.query(Transaction).all()

    # Skapa en lista med giltiga IBAN från kontotabellen
    valid_ibans = {a.iban for a in session.query(Account).all()}

    validation_results = []
    for tx in transactions:
        is_valid = True
        reason = "OK"

        # Kontrollera att både avsändare- och mottagarkonton existerar
        if tx.sender_account not in valid_ibans or tx.receiver_account not in valid_ibans:
            is_valid = False
            reason = "Ogiltigt IBAN"

        # Validera valuta
        if tx.currency not in ALLOWED_CURRENCIES:
            is_valid = False
            reason = "Ogiltig valuta"

        # Validera transaktionsbelopp
        if tx.amount <= 0:
            is_valid = False
            reason = "Felaktigt belopp"

        validation_results.append({
            "transaction_id": tx.id,
            "is_valid": is_valid,
            "validation_reason": reason
        })

    session.close()

    # Spara valideringsresultat
    with open(f"{CHECKPOINT_DIR}/validation_results.json", "w") as f:
        json.dump(validation_results, f, indent=2)

    return validation_results