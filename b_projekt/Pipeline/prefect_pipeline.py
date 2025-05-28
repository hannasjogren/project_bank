#Automatiserad pipeline
#Ändra LOG_FILE till er egna filväg
import logging
from Pipeline.main_flow import import_customers, import_accounts, import_transactions
from prefect import flow, task

# Loggning – Skriver både till fil och konsol
LOG_FILE = r"C:\Users\hanna\PycharmProjects\b_projekt\Logs\prefect_pipeline.log"
logger = logging.getLogger("PrefectPipeline")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE) #permanenta loggar som kan analyseras i efterhand
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler() #Loggar skrivs ut direkt till terminalen medan programmet körs
stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(stream_handler)

@task(name="Import Customers")
def run_import_customers():
    logger.info("Startar import av kunder.")
    import_customers()
    logger.info("Import av kunder klar.")

@task(name="Import Accounts")
def run_import_accounts():
    logger.info("Startar import av konton.")
    import_accounts()
    logger.info("Import av konton klar.")

@task(name="Import Transactions")
def run_import_transactions():
    logger.info("Startar import av transaktioner.")
    import_transactions()
    logger.info("Import av transaktioner klar.")

@task(name="Transform Data")
def transform_data():
    logger.info("Startar datatransformering.")
    # Lägg till transformering här vid behov
    pass
    logger.info("Datatransformering klar.")

@task(name="Export Data")
def export_data():
    logger.info("Startar dataexport.")
    # Lägg till exportfunktion här vid behov
    pass
    logger.info("Dataexport klar.")

@flow(name="Bank Task Pipeline")
def task_pipeline():
    logger.info("Startar hela pipeline-flödet.")
    run_import_customers()
    run_import_accounts()
    run_import_transactions()
    transform_data()
    export_data()
    logger.info("Hela pipelinen är slutförd.")

if __name__ == "__main__":
    task_pipeline()