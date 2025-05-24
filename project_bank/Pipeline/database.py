#DB-konfiguration, filvägar, SQLAlchemy och Engine

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Pipeline.database import Base

DATABASE_URL = "postgresql+psycopg2://username:password@localhost:5432/your_database"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

#Returnerar en ny databas-session
def get_session():
    return SessionLocal()

CUSTOMER_CSV = "data/customers.csv"
TRANSACTION_CSV = "data/transactions.csv"

LOG_FILE = "logs/pipeline.log"
EXPECTATION_SUITE_PATH = "expectations/transaction_expectations.json"


#SQLAlchemy och Engine
import pandas as pd
from Pipeline.logging_setup import logger

def get_engine():
    return create_engine(DATABASE_URL)

def store_validation_results(results: pd.DataFrame):
    try:
        engine = get_engine()
        results.to_sql("validation_logs", engine, if_exists="append", index=False)
        logger.info("Valideringsresultat lagrade i databasen.")
    except Exception as e:
        logger.error("Kunde inte lagra valideringsresultat: %s", str(e))
        raise