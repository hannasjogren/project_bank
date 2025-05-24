#Version B — Stopp direkt vid okänt konto, avvisa transaktionen omgående
'''Fördelar:
Enkelhet: Klar och tydlig logik som direkt förhindrar ogiltiga transaktioner.
Dataintegritet: Endast giltiga transaktioner sparas i systemet.
Snabb feedback: Användaren eller systemet får direkt besked om fel.
Lägre underhåll: Ingen separat tabell för "pending" data och färre edge cases att hantera.

Nackdelar:
Ingen spårbarhet: Transaktionen försvinner helt och hållet utan någon loggning, vilket kan göra felsökning svårare.
Inget stöd för återkommande verifiering: Om kontot skapas senare måste transaktionen initieras igen.
Användarupplevelse: Kan kännas abrupt eller otydligt om feedback inte hanteras väl i UI.'''

def validate_account_exists(account_id: str, db) -> bool:
    from Models.account import Account
    return db.query(Account).filter(Account.id == account_id).first() is not None

def validate_transaction_input(tx: dict, db):
    if not validate_account_exists(tx["sender_account"], db):
        raise ValueError("Avsändarkonto saknas")
    if not validate_account_exists(tx["receiver_account"], db):
        raise ValueError("Mottagarkonto saknas")

"""
Validerar överföringar mellan konton.
Kontrollerar t.ex. saldo, negativa belopp och valutaöverensstämmelse.
"""

def validate_transfer(sender, receiver, amount):
    errors = []

    if amount <= 0:
        errors.append("Belopp måste vara positivt")

    if sender.balance < amount:
        errors.append("Otillräckligt saldo på avsändarkonto")

    if sender.currency_code != receiver.currency_code:
        errors.append("Valutor för avsändare och mottagare matchar inte")

    return errors