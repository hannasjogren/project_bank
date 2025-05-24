#Logging till fil och stdout
import logging
from Pipeline.database import LOG_FILE

logger = logging.getLogger("pipeline_logger")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
