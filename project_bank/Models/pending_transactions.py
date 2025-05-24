#Version A — Logga okända konton i separat tabell
#Modell för transaktioner som ligger i vänteläge för manuell granskning.
#Innehåller info om status och orsaker till delay.
'''Fördelar:
Flexibel hantering: Ingen transaktion försvinner. Sparar alla försök med okända konton för senare manuell granskning eller återkoppling.
Spårbarhet: Det finns en tydlig historik över alla avvisade försök, vilket kan ge värdefull insikt.
Minskad risk: Systemet kraschar eller blockerar inte flödet. Hantering kan ske asynkront.
Automatiseringsmöjligheter: Kan senare byggas ut med notifieringar, arbetsflöden eller återkommande kontroller.

Nackdelar:
Komplexitet: Kräver extra logiktjänster, databastabell och process för att hantera dessa väntande transaktioner.
Fördröjning: Transaktionen blir inte direkt slutförd eller avvisad. Kräver manuell eller automatisk granskning innan den kan hanteras.
Lagringskostnad: Ökar databasstorlek över tid med potentiellt många väntande poster.'''

from sqlalchemy import Column, String, Boolean, DateTime, Integer
from datetime import datetime, timezone
from Pipeline.database import Base

class PendingTransaction(Base):
    __tablename__ = "pending_transactions"

    id = Column(String, primary_key=True)
    sender_account = Column(String)
    receiver_account = Column(String)
    amount = Column(Integer)
    currency = Column(String(3))
    reason = Column(String, nullable=False)
    status = Column(String(20), default='pending')  # pending, approved, rejected
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    reviewed = Column(Boolean, default=False)

    def __repr__(self):
        return f"<PendingTransaction(id={self.id}, amount={self.amount}, status={self.status})>"
