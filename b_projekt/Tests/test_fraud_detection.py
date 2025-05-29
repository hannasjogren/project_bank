import pytest
import logging
from Pipeline.database import SessionLocal
from Models.transaction import Transaction

@pytest.fixture(scope="module")
def session():
    return SessionLocal()

# Ändra log_file till er egna filväg
def setup_logger(test_name):
    log_file = f"C:\\Users\\hanna\\PycharmProjects\\b_projekt\\Logs\\{test_name}_logs.log"
    logger = logging.getLogger(test_name)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)

    return logger

def test_fraud_detection(session):
    logger = setup_logger("fraud_detection_test")

    suspicious_tx = session.query(Transaction).filter(Transaction.amount > 10000).all()

    assert isinstance(suspicious_tx, list), "Felaktig typ på resultat!"
    logger.info(f"Test Passed: {len(suspicious_tx)} misstänkta transaktioner identifierade.")