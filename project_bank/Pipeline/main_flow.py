#Prefect-flöde: laddning → validering → export
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import IntervalSchedule
from datetime import timedelta
from prefect import flow, task
from Pipeline.main_flow import main_flow
import pandas as pd
from pathlib import Path
import os
import json
import great_expectations as ge
from sqlalchemy import create_engine
from datetime import datetime
import logging

# Konfiguration
CUSTOMER_CSV = "data/customers.csv"
TRANSACTION_CSV = "data/transactions.csv"
CHECKPOINT_DIR = "checkpoints"
LOG_FILE = "pipeline.log"
ALLOWED_CURRENCIES = {"SEK", "USD", "EUR", "DKK", "JPY", "ZMW", "NOK", "ZAR", "RMB", "GBP"}

# PostgreSQL URI
DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/dbname"

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


@task
def read_customer_csv(file_path: str) -> pd.DataFrame:
    logging.info("Läser in kunddata")
    return pd.read_csv(file_path, header=None, names=[
        "name", "address", "phone", "personal_id", "account_number"
    ])


@task
def read_transaction_csv(file_path: str) -> pd.DataFrame:
    logging.info("Läser in transaktionsdata")
    return pd.read_csv(file_path, header=None, names=[
        "id", "timestamp", "amount", "currency", "from_account", "to_account",
        "from_country", "from_city", "to_country", "to_city", "direction", "description"
    ])


@task
def validate_accounts(transactions: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    logging.info("Validerar IBAN i transaktioner mot kunddata")
    valid_accounts = set(customers["account_number"])
    mask = transactions["from_account"].isin(valid_accounts) & transactions["to_account"].isin(valid_accounts)
    valid_tx = transactions[mask].copy()
    invalid_tx = transactions[~mask]

    if not invalid_tx.empty:
        logging.warning(f"{len(invalid_tx)} ogiltiga transaktioner hittades (saknar matchande konton).")
    return valid_tx


@task
def run_ge_validation(transactions: pd.DataFrame) -> dict:
    logging.info("Kör Great Expectations validering")
    df = ge.from_pandas(transactions)

    df.expect_column_values_to_be_in_set("currency", list(ALLOWED_CURRENCIES))
    df.expect_column_values_to_not_be_null("id")
    df.expect_column_values_to_be_of_type("amount", "float")
    df.expect_column_values_to_be_between("amount", min_value=0.0, max_value=None)
    result = df.validate()

    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    with open(Path(CHECKPOINT_DIR) / "ge_validation_result.json", "w") as f:
        json.dump(result, f, indent=2)

    return result


@task
def save_validation_to_db(result: dict):
    logging.info("Sparar valideringsresultat i PostgreSQL")

    rows = [{
        "validation_time": datetime.now(),
        "success": result["success"],
        "evaluated_expectations": len(result["results"]),
        "unexpected_count": sum(r["result"].get("unexpected_count", 0) for r in result["results"]),
    }]

    df = pd.DataFrame(rows)

    engine = create_engine(DATABASE_URL)
    try:
        df.to_sql("validation_logs", con=engine, if_exists="append", index=False)
        logging.info("Valideringsdata sparad i databas.")
    except Exception as e:
        logging.error(f"Misslyckades med att spara i DB: {e}")
        raise


@task
def create_transaction_checkpoints(transactions: pd.DataFrame):
    logging.info("Skapar checkpoints per transaktion")
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    for _, row in transactions.iterrows():
        checkpoint_file = Path(CHECKPOINT_DIR) / f"{row['id']}.ge.json"
        checkpoint_data = {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "from_account": row["from_account"],
            "to_account": row["to_account"],
            "amount": row["amount"],
            "description": row["description"] or "N/A"
        }
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint_data, f, indent=2)


@flow(name="PostgreSQL och logging pipeline")
def data_import_pipeline():
    try:
        customers = read_customer_csv(CUSTOMER_CSV)
        transactions = read_transaction_csv(TRANSACTION_CSV)
        valid_transactions = validate_accounts(transactions, customers)
        validation_result = run_ge_validation(valid_transactions)
        save_validation_to_db(validation_result)

        if validation_result["success"]:
            logging.info("Validering OK – checkpoints skapas.")
            create_transaction_checkpoints(valid_transactions)
        else:
            logging.warning("Validering misslyckades – inga checkpoints skapas.")
    except Exception as e:
        logging.exception("Fel under körning av pipeline")
        raise


if __name__ == "__main__":
    data_import_pipeline()

deployment = Deployment.build_from_flow(
    flow=main_flow,
    name="Scheduled-Validation",
    schedule=IntervalSchedule(interval=timedelta(hours=1)), #Konfigurerar flödet att köras varje timme
    work_queue_name="default"
)

if __name__ == "__main__":
    deployment.apply()

#komplett Prefect-pipeline med validering och GE
