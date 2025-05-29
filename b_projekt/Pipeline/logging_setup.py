#Ändra LOG_FILE= path efter behov
#Importera loggningen i flera filer utan att behöva sätta upp logging på nytt
#Praktiskt att ha en separat loggfil så att alla kan använda den direkt

import logging
import os

# Konfigurera loggfilens sökväg
LOG_DIR = r"C:\Users\hanna\PycharmProjects\b_projekt\Logs"
LOG_FILE = os.path.join(LOG_DIR, "pipeline.log")

# Kontrollera om loggmappen finns, annars skapa den
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Kontrollera att loggfilen kan skrivas till
try:
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)
except Exception as e:
    raise Exception(f"Kan inte skapa loggfil: {e}")

# Stream logging till konsolen
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(stream_handler)

# Testloggning
logger.info("Loggningssystemet är korrekt konfigurerat!")