import pandas as pd
import pytest
import logging
import os
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


def test_transaction_export(session):
    logger = setup_logger("transaction_export")

    transactions = session.query(Transaction).all()

    df = pd.DataFrame([t.__dict__ for t in transactions])
    df.drop(columns=["_sa_instance_state"], errors="ignore", inplace=True)

    assert not df.empty, "Export ska innehålla data!"

    # Skapa exportmappen med nedan om den inte finns och använd er filväg
    export_dir = r"C:\Users\hanna\PycharmProjects\b_projekt\Exports"
    export_path = os.path.join(export_dir, "transactions_export.csv")

    if not os.path.exists(export_path):
        os.makedirs(export_dir)

    df.to_csv(export_path, index=False, encoding="utf-8")

    exported_df = pd.read_csv(export_path)
    assert not exported_df.empty, "Exporterade filen ska ha data!"

    logger.info(f"Test Passed: Exporterade {len(df)} transaktioner till {export_path}")