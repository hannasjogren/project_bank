import pickle
import psycopg2

conn = psycopg2.connect(
    dbname="test_bank_application",
    user="postgres",
    password="my-container123",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Mappning från något fält till account_id om du fortfarande behöver matcha konton
account_lookup = {}

try:
    # -------- Importera kunder -------- #
    with open("data/customers_cleaned.pkl", "rb") as c:
        reader = pickle.load(c)

        cur.execute("BEGIN;")

        for row in reader:
            cur.execute("""
                INSERT INTO customers (customer, personnummer, phone, address)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (row["Customer"], row["Personnummer"], row.get("Phone"), row["Address"]))
            customer_id = cur.fetchone()[0]

            # Skapa bankkonto utan iban
            cur.execute("""
                INSERT INTO bank_accounts (customer_id)
                VALUES (%s)
                RETURNING id;
            """, (customer_id,))
            account_id = cur.fetchone()[0]

            # Om du fortfarande behöver matcha med någon typ av ID (ex. BankAccount-nummer)
            account_lookup[row["BankAccount"]] = account_id

        conn.commit()
        print("Customers and bank accounts inserted successfully.")

except Exception as e:
    conn.rollback()
    print("Error during customer insert:", e)

try:
    # -------- Importera transaktioner från pickle -------- #
    with open("data/cleaned_transaction.pk1", "rb") as f:
        transactions_file = pickle.load(f)

    transactions_file = transactions_file.to_dict(orient="records")

    cur.execute("BEGIN;")

    for tx in transactions_file:
        cur.execute("""
            INSERT INTO transactions (
                transaction_id, timestamp, amount, currency, 
                sender_account, receiver_account, sender_country, 
                sender_municipality, receiver_country, 
                receiver_municipality, transaction_type, notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            tx["transaction_id"],
            tx["timestamp"],
            tx["amount"],
            tx["currency"],
            account_lookup.get(tx["sender_account"]),
            account_lookup.get(tx["receiver_account"]),
            tx["sender_country"],
            tx["sender_municipality"],
            tx["receiver_country"],
            tx["receiver_municipality"],
            tx["transaction_type"],
            tx.get("notes", "")
        ))

    conn.commit()
    print("Transactions inserted successfully.")

except Exception as e:
    conn.rollback()
    print("Error during transaction insert:", e)

finally:
    cur.close()
    conn.close()
