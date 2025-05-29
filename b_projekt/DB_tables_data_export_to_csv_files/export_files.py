import os
import pandas as pd
from sqlalchemy import create_engine

# PostgreSQL-anslutning
DATABASE_URL = "postgresql://hanna:pass123@localhost:5433/bankprojekt"
engine = create_engine(DATABASE_URL)

# Ny exportmapp
EXPORT_FOLDER = r"C:\Users\hanna\PycharmProjects\b_projekt\DB_tables_data_export_to_csv_files"
os.makedirs(EXPORT_FOLDER, exist_ok=True)

# Hämta alla tabeller
query = "SELECT tablename FROM pg_tables WHERE schemaname='public';"
tables = pd.read_sql(query, engine)

# Exportera varje tabell till CSV
for table in tables["tablename"]:
    df = pd.read_sql(f"SELECT * FROM {table}", engine)
    export_path = os.path.join(EXPORT_FOLDER, f"{table}.csv")
    df.to_csv(export_path, index=False)
    print(f"Exporterat: {export_path}")