import pytest
import logging
import re
from Pipeline.database import SessionLocal
from Models.customer import Customer


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


def test_phone_number_format(session):
    logger = setup_logger("validation_test")

    customers = session.query(Customer).all()

    phone_regex = re.compile(r"^\+?[0-9\s()-]+$")
    for customer in customers:
        assert phone_regex.match(customer.phone), f"Fel format på telefonnummer: {customer.phone}"

    logger.info("Test Passed: Alla telefonnummer har korrekt format.")