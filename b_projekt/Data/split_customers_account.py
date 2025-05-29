# Ändra till er egen filväg
import pandas as pd

CUSTOMER_CSV = r"C:\Users\hanna\PycharmProjects\b_projekt\Data\sebank_customers_with_accounts.csv"
CUSTOMERS_OUTPUT = r"C:\Users\hanna\PycharmProjects\b_projekt\Data\customers.csv"
ACCOUNTS_OUTPUT = r"C:\Users\hanna\PycharmProjects\b_projekt\Data\accounts.csv"

def split_customers_and_accounts():
# Läs in originalfilen
    df = pd.read_csv(CUSTOMER_CSV, encoding="utf-8")

# Skapa customer.csv utan IBAN och ta bort dubbletter
    customers_df = df[['Customer', 'Address', 'Phone', 'Personnummer']].drop_duplicates()
    customers_df.to_csv(CUSTOMERS_OUTPUT, index=False, encoding="utf-8")

# Skapa accounts.csv med IBAN och Personnummer
    accounts_df = df[['Personnummer', 'BankAccount']].rename(columns={'BankAccount': 'iban'})
    accounts_df.to_csv(ACCOUNTS_OUTPUT, index=False, encoding="utf-8")

    print(f"Filer skapade: {CUSTOMERS_OUTPUT} och {ACCOUNTS_OUTPUT}")
    print(f"Antal kunder: {len(customers_df)}, antal konton: {len(accounts_df)}")

if __name__ == "__main__":
    split_customers_and_accounts()