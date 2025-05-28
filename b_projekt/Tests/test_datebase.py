import pytest
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from Pipeline.database import Base

# Direkt definierad testdatabas
# Ändra user, password och portväg till er egna
# Skapa en testdatabas i postgreSQL konsol om det skulle kärva innan ni kör igenom test_datebase.py
# CREATE DATABASE bankprojekt_test;
DATABASE_URL = "postgresql+psycopg2://hanna:pass123@localhost:5433/bankprojekt_test"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Skapa tabeller i testdatabasen
Base.metadata.create_all(engine)

@pytest.fixture(scope="module")
def session():
    test_session = SessionLocal()
    yield test_session
    test_session.close()

# Ändra log_file till er egna filväg
def setup_logger(test_name):
    log_file = f"C:\\Users\\hanna\\PycharmProjects\\b_projekt\\Logs\\{test_name}_logs.log"
    logger = logging.getLogger(test_name)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)

    return logger

def test_database_connection(session):
    logger = setup_logger("database_test")

    try:
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1, "Testdatabasen fungerar inte korrekt!"
        logger.info("Test Passed: Testdatabasen är ansluten och svarar korrekt.")
    except Exception as e:
        logger.error(f"Test Failed: Kunde inte ansluta till testdatabasen - {str(e)}")
        pytest.fail("Testdatabasanslutning misslyckades!")