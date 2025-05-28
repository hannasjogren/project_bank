#Ändra LOG_FILE= path efter behov
#Importera loggningen i flera filer utan att behöva sätta upp logging på nytt
#Praktiskt att ha en separat loggfil så att alla kan använda den direkt

"""
import logging

LOG_FILE = r"C:\Users\hanna\PycharmProjects\b_projekt\Logs\pipeline.log"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(stream_handler)"""