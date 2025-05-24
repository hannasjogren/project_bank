#Testa databasanslutningen
from Pipeline.database import get_engine

def test_database_connection():
    engine = get_engine()
    with engine.connect() as connection:
        assert connection is not None
