from prefect import flow, task
import pandas as pd
from sqlalchemy import create_engine

@task
def import_csv(csv_path):
    dataframe = pd.read_csv(csv_path)
    return dataframe

@task
def write_to_postgres(dataframe, table_name, db_url):
    engine = create_engine(db_url)
    dataframe.to_sql(table_name, engine, if_exists='append', index=False, method='multi')

@flow
def load_customers_flow():
    dataframe = import_csv(r"C:\Users\hanna\Projects\project_bank\project_bank\Data\sebank_customers_with_accounts.csv")
    write_to_postgres(dataframe, "customers_with_accounts", "postgresql://hanna:pass123@localhost:5433/bankprojekt")

@flow
def load_transactions_flow():
    dataframe = import_csv(r"C:\Users\hanna\Projects\project_bank\project_bank\Data\transaction_filtered.csv")
    write_to_postgres(dataframe, "transactions", "postgresql://hanna:pass123@localhost:5433/bankprojekt")

@flow
def main_flow():
    load_customers_flow()
    load_transactions_flow()

if __name__ == "__main__":
    main_flow()
