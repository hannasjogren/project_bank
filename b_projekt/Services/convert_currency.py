#Hanterar valutakonvertering baserat på ExchangeRate
from sqlalchemy.orm import Session
from Models.exchange_rate import ExchangeRate

def convert_currency(session: Session, amount: float, from_currency: str, to_currency: str) -> float:
    rate = session.query(ExchangeRate).filter_by(currency_from=from_currency, currency_to=to_currency).first()
    if not rate:
        raise ValueError(f"Växelkurs saknas för {from_currency} → {to_currency}")
    return amount * rate.rate