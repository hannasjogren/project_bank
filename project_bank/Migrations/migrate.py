import psycopg2
from Pipeline.database import DATABASE_URL
from Pipeline.logging_setup import logger

def run_migrations():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        with open("Migrations/create_validation_table.py", "r") as f:
            cur.execute(f.read())
        conn.commit()
        logger.info("Databasmigrering slutförd.")
    except Exception as e:
        logger.critical("Migrering misslyckades: %s", str(e))
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    run_migrations()