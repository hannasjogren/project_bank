#Version C – Försök att överföra till okänt konto → loggas till pending_transactions och transaktionen stoppas
'''Fördelar:
Bäst av båda världar: Transaktionen stoppas direkt för dataintegritet men varje fel registreras för uppföljning.
Spårbarhet: Alltid logg över misslyckade försök.
Underlättar felsökning: Systemansvariga kan analysera och agera på problem utan att förlita sig på användaråterkoppling.
Möjlighet till automatiserad hantering: Kan senare implementeras workflows för att hantera "pending" automatiskt.

Nackdelar:
Mer komplex implementation: Kräver extra resurser för att både hantera fel och hålla pending-tabell uppdaterad.
Dubbel datalagring: Fel transaktioner sparas i två system. Kan bli lite redundans.
Ökad databasvolym: Precis som version A, kan tabellen med väntande transaktioner växa snabbt.'''

import uuid
from datetime import datetime, timezone
from Models.pending_transactions import PendingTransaction

def handle_transaction(tx: dict, db):
    from Models.account import Account
    receiver = db.query(Account).filter(Account.id == tx["receiver_account"]).first()

    if not receiver:
        pending = PendingTransaction(
            id=str(uuid.uuid4()),
            sender_account=tx["sender_account"],
            receiver_account=tx["receiver_account"],
            amount=tx["amount"],
            currency=tx["currency"],
            reason="Mottagarkonto saknas",
            created_at=datetime.now(timezone.utc)
        )
        db.add(pending)
        db.commit()
        raise ValueError("Transaktion avbruten – mottagarkonto finns ej.")
    
    # annars fortsätt med transaktionen
    
"""
Hanterar transaktioner med validering, fraud-detektion och uppdatering.

Sparar transaktioner i DB eller lägger till i väntelista om misstänkt.
"""

from Pipeline.database import get_session
from Models import transaction, account, PendingTransaction
from Models.blacklist import detect_fraud
from transfer_validation import validate_transfer

def process_transaction(session, sender_iban, receiver_iban, amount, currency_code):
    """
    Hantera en transaktion med validering, fraud detection och uppdatering av kontobalanser.

    Parametrar:
    - session: SQLAlchemy-databassession
    - sender_iban: IBAN för avsändarkonto (str)
    - receiver_iban: IBAN för mottagarkonto (str)
    - amount: belopp som ska överföras (float)
    - currency_code: valutakod, t.ex. 'SEK', 'USD' (str)

    Returnerar:
    - transaction: Transaction-objekt som sparats i databasen
    - is_fraud: bool, om transaktionen flaggats som misstänkt
    - reason: str eller None, orsak till fraud-flagga
    """

    sender = session.query(account).filter(account.iban == sender_iban).first()
    receiver = session.query(account).filter(account.iban == receiver_iban).first()

    if not sender or not receiver:
        raise ValueError("Avsändar- eller mottagarkonto saknas i databasen")

    blacklist_ibans = {b.iban for b in session.query(transaction).all()}

    errors = validate_transfer(sender, receiver, amount)
    if errors:
        raise ValueError(f"Valideringsfel: {errors}")

    transaction = transaction(
        sender_iban=sender_iban,
        receiver_iban=receiver_iban,
        amount=amount,
        currency_code=currency_code
    )

    is_fraud, reason = detect_fraud(transaction, blacklist_ibans)
    transaction.is_fraud = is_fraud
    transaction.fraud_reason = reason

    if is_fraud:
        pending = PendingTransaction(
            sender_iban=sender_iban,
            receiver_iban=receiver_iban,
            amount=amount,
            currency_code=currency_code,
            status='pending'
        )
        session.add(pending)
    else:
        sender.balance -= amount
        receiver.balance += amount
        session.add(transaction)

    session.commit()

    return transaction, is_fraud, reason