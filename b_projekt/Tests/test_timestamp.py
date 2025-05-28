import pytest
import logging
import pandas as pd
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


def test_timestamp_format(session):
    logger = setup_logger("timestamp_test")

    transactions = session.query(Transaction).all()

    for tx in transactions:
        assert isinstance(pd.to_datetime(tx.timestamp), pd.Timestamp), "Felaktig tidsstämpel!"

    logger.info(f"Test Passed: Alla tidsstämplar är korrekt formaterade.")