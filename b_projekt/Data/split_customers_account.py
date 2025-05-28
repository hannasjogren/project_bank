#Ändra till er egna filväg
import pandas as pd

CUSTOMER_CSV = r"C:\Users\hanna\PycharmProjects\b_projekt\Data\sebank_customers_with_accounts.csv"
CUSTOMERS_OUTPUT = r"C:\Users\hanna\PycharmProjects\b_projekt\Data\customers.csv"
ACCOUNTS_OUTPUT = r"C:\Users\hanna\PycharmProjects\b_projekt\Data\accounts.csv"

def split_customers_and_accounts():
    customers_df = pd.read_csv(CUSTOMER_CSV)

    # Skriv ut kolumnnamnen för felsökning
    print(customers_df.columns)

    # Justerade kolumnnamn baserat på CSV-strukturen
    customers_df[["Customer", "Address", "Phone", "Personnummer"]].to_csv(CUSTOMERS_OUTPUT, index=False)
    customers_df[["BankAccount"]].to_csv(ACCOUNTS_OUTPUT, index=False)

    print(f"Splittade {len(customers_df)} kunder och konton!")

if __name__ == "__main__":
    split_customers_and_accounts()