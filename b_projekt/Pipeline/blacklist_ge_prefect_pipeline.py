import pandas as pd
import os
import logging
import great_expectations as ge
from sqlalchemy import text
from prefect import task, flow
from Pipeline.database import SessionLocal, Base, engine
from Models.blacklist import Blacklist

# Loggning
LOG_FILE = r"C:\Users\hanna\PycharmProjects\b_projekt\Logs\blacklist_import.log"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(stream_handler)

BLACKLIST_CSV = r"C:\Users\hanna\PycharmProjects\b_projekt\Exports\blacklist.csv"


@task
def check_database():
    """Kontrollerar databasanslutningen innan importen."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Databasanslutningen är korrekt")
    except Exception as db_error:
        raise Exception(f"Databasanslutningen misslyckades: {db_error}")


@task
def create_tables():
    """Skapar tabeller om de inte redan finns."""
    Base.metadata.create_all(bind=engine)
    logger.info("Tabeller har skapats")


@task
def read_csv():
    """Läser in och validerar CSV-filen."""
    if not os.path.exists(BLACKLIST_CSV) or os.stat(BLACKLIST_CSV).st_size == 0:
        logger.warning("Ingen data i blacklist.csv, avbryter import")
        return None

    df = pd.read_csv(BLACKLIST_CSV, encoding="utf-8")

    # Hantera `NaN`-värden genom att ersätta dem med "Unknown"
    df["sender_country"] = df["sender_country"].fillna("Unknown").astype(str)
    df["receiver_country"] = df["receiver_country"].fillna("Unknown").astype(str)

    required_columns = ["account_iban", "reason", "amount", "sender_country", "receiver_country"]
    if not all(col in df.columns for col in required_columns):
        logger.error(f"Saknade kolumner i CSV: {set(required_columns) - set(df.columns)}")
        return None

    logger.info(f"CSV-fil läst in: {len(df)} rader")
    return df


@task
def validate_data(df):
    """Validerar data med Great Expectations."""
    if df is None:
        logger.error("Ingen giltig data att validera")
        return None

    df_ge = ge.from_pandas(df)

    expectations = [
        df_ge.expect_column_values_to_not_be_null("account_iban"),
        df_ge.expect_column_values_to_not_be_null("reason"),
        df_ge.expect_column_values_to_be_between("amount", min_value=0, max_value=1_000_000),
        df_ge.expect_column_values_to_match_regex("account_iban", r"^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$")
    ]

    failed_checks = [exp for exp in expectations if not exp.success]

    if failed_checks:
        logger.error(f"Validering misslyckades. Problem med {len(failed_checks)} kontroller")
        for check in failed_checks:
            logger.error(f"Fel: {check.expectation_config['expectation_type']}")
        return None

    logger.info("All data är validerad")
    return df


@task
def import_blacklist(df):
    """Importerar data till `blacklist`-tabellen."""
    if df is None:
        logger.error("Ingen giltig data att importera")
        return

    with SessionLocal() as session:
        for _, row in df.iterrows():
            # Kontrollera om IBAN redan finns
            existing_entry = session.query(Blacklist).filter_by(account_iban=row["account_iban"]).first()

            if existing_entry:
                logger.info(f"Konto {row['account_iban']} finns redan i blacklist. Hoppar över")
                continue

            logger.info(f"Importerar konto: {row.to_dict()}")
            session.add(Blacklist(
                account_iban=row["account_iban"],
                reason=row["reason"],
                amount=row["amount"],
                sender_country=row["sender_country"],
                receiver_country=row["receiver_country"]
            ))

        session.commit()
        logger.info("Svartlistning importerad")


@flow(name="Blacklist Import Flow")
def main_flow():
    """Huvudflödet för att skapa `blacklist`-tabellen, validera och importera CSV-data."""
    check_database()
    create_tables()
    df = read_csv()
    df_valid = validate_data(df)  # Validera datan först
    import_blacklist(df_valid)
    logger.info("Svartlistningsflödet är genomfört")


if __name__ == "__main__":
    main_flow()