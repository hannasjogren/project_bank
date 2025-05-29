from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Databasanslutning
DATABASE_URL = "postgresql+psycopg2://hanna:pass123@localhost:5433/bankprojekt"
engine = create_engine(DATABASE_URL)

# Skapa session och basmodell
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Kontroll av databasanslutning
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))  # Testa anslutningen
except Exception as e:
    raise Exception(f"Databasanslutningen misslyckades: {e}")

print("Databasanslutningen är korrekt!")