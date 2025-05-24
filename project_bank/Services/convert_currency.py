"""
Konverterar ett belopp från en valuta till en annan baserat på ExchangeRate-tabellen.
-db: aktiv SQLAlchemy-session
- amount: belopp att konvertera
- from_currency: valutakod att konvertera från (t.ex. "USD")
- to_currency: valutakod att konvertera till (t.ex. "SEK")
Returnerar:
- Det konverterade beloppet som float
Undantag:
- ValueError om växelkurs saknas"""

import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from Models.exchange_rate import ExchangeRate

#Konvertering av valuta är en affärslogisk operation, som kräver databasaccess och beräkningar
#convert_currency är en funktion som använder datan medan ExchangeRate är mer databasstruktur och regler
def convert_currency(db: Session, amount: float, from_currency: str, to_currency: str) -> float:

    if from_currency == to_currency:
        return amount  # Ingen konvertering behövs

    rate_entry = db.query(ExchangeRate).filter_by(
        from_currency=from_currency.upper(),
        to_currency=to_currency.upper()
    ).first()

    if not rate_entry:
        raise ValueError(f"Missing exchange rate from {from_currency} to {to_currency}")

    return round(amount * rate_entry.rate, 2)


rates = {
    'SEK': 1.0,
    'USD': 10.5,
    'EUR': 11.2
}

def convert_to_sek(amount, currency):
    return amount * rates.get(currency, 1.0)