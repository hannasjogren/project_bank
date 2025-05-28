from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Databasanslutning
# Ändra hanna:pass123@localhost:5433/bankprojekt i DATABASE_URL till er egna databas
DATABASE_URL = "postgresql+psycopg2://hanna:pass123@localhost:5433/bankprojekt"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Importera modeller så att tabellerna skapas
from Models.customer import Customer
from Models.account import Account
from Models.transaction import Transaction
from Models.pending_transaction import PendingTransaction


# Skapa tabeller i databasen
Base.metadata.create_all(engine)