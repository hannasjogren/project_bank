import pandas as pd
from sqlalchemy import create_engine
from Pipeline.database import DATABASE_URL

engine = create_engine(DATABASE_URL)
df = pd.read_sql('SELECT * FROM validation_logs', engine)
df.to_csv('validation_results.csv', index=False)
