"""Filtrerar bort transaktioner där avsändare- och mottagarland är samma, vilket minskar falska flaggningar
Identifierar konton som gör flera stora transaktioner inom kort tid, vilket kan vara misstänkt
Höjt beloppsgränsen till 100,000, så att små transaktioner inte överflaggas
Lägger till konton med hög transaktionsfrekvens som ett extra svartlistningskriterium"""

import pandas as pd
import os
import logging

# Filvägar
DATA_DIR = r"C:\Users\hanna\PycharmProjects\b_projekt\Data"
EXPORT_DIR = r"C:\Users\hanna\PycharmProjects\b_projekt\Exports"

TRANSACTIONS_CSV = os.path.join(DATA_DIR, "transactions.csv")
BLACKLIST_CSV = os.path.join(EXPORT_DIR, "blacklist.csv")
LOG_FILE = os.path.join(r"C:\Users\hanna\PycharmProjects\b_projekt\Logs", "blacklist_export.log")

# Setup logger
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Svartlistningskriterier
SUSPICIOUS_AMOUNT_THRESHOLD = 100000  # Höjer beloppsgränsen
HIGH_RISK_TRANSACTION_COUNT = 100  # Länder med fler än 100 transaktioner flaggas
TOTAL_ACCOUNT_THRESHOLD = 1_000_000  # Om ett konto skickat/mottagit mer än 1M, flaggas det
HIGH_FREQUENCY_THRESHOLD = 5  # Om ett konto gör 5 stora transaktioner inom kort tid, flaggas det

# Läs transaktionsdata från CSV
try:
    df = pd.read_csv(TRANSACTIONS_CSV, encoding="utf-8")
except FileNotFoundError:
    logger.error(f"Fil saknas: {TRANSACTIONS_CSV}")
    print(f"Fel: {TRANSACTIONS_CSV} hittades inte.")
    exit()

# Kontrollera att CSV-filen inte är tom
if df.empty:
    logger.warning(f"{TRANSACTIONS_CSV} är tom. Avbryter svartlistning.")
    print("Fel: Transaktionsfilen är tom. Inga svartlistade konton skapades.")
    exit()

# Dynamiskt identifiera högriskländer baserat på transaktionsfrekvens
country_risk_counts = df[["sender_country", "receiver_country"]].stack().value_counts()
HIGH_RISK_COUNTRIES = set(country_risk_counts[country_risk_counts > HIGH_RISK_TRANSACTION_COUNT].index)

logger.info(f"Högriskländer identifierade: {HIGH_RISK_COUNTRIES}")
print(f"Dynamiskt identifierade högriskländer: {HIGH_RISK_COUNTRIES}")

# Filtrera transaktioner baserat på kriterier
suspicious_df = df[
    (df["amount"] > SUSPICIOUS_AMOUNT_THRESHOLD) |
    (df["receiver_country"].isin(HIGH_RISK_COUNTRIES)) |
    (df["sender_country"].isin(HIGH_RISK_COUNTRIES))
    ]

# Filtrera bort transaktioner där avsändare- och mottagarland är samma
suspicious_df = suspicious_df[suspicious_df["sender_country"] != suspicious_df["receiver_country"]]

# Identifiera konton som gör flera stora transaktioner inom kort tid
df["timestamp"] = pd.to_datetime(df["timestamp"])  # Konvertera timestamp till datetime-format
df = df.sort_values(by=["sender_account", "timestamp"])  # Sortera efter konto och tid
df["time_diff"] = df.groupby("sender_account")["timestamp"].diff().dt.total_seconds().fillna(0)  # Beräkna tidsdifferens

high_frequency_accounts = df[(df["amount"] > SUSPICIOUS_AMOUNT_THRESHOLD) & (df["time_diff"] < 86400)] \
    .groupby("sender_account").size().reset_index(name="transaction_count")
high_frequency_accounts = \
high_frequency_accounts[high_frequency_accounts["transaction_count"] > HIGH_FREQUENCY_THRESHOLD][
    "sender_account"].tolist()

# Lägg till konton med höga transaktionsfrekvenser i svartlistningen
extra_suspicious_df = df[df["sender_account"].isin(high_frequency_accounts)]
suspicious_df = pd.concat([suspicious_df, extra_suspicious_df]).drop_duplicates()

# Skapa `blacklist.csv`
if not suspicious_df.empty:
    blacklist_df = suspicious_df[
        ["sender_account", "transaction_type", "amount", "sender_country", "receiver_country"]].drop_duplicates()
    blacklist_df.rename(columns={"sender_account": "account_iban", "transaction_type": "reason"}, inplace=True)

    # Skapa exportmappen om den inte finns
    os.makedirs(EXPORT_DIR, exist_ok=True)

    # Skriv till CSV
    blacklist_df.to_csv(BLACKLIST_CSV, index=False, encoding="utf-8")

    logger.info(f"Svartlistning klar! {len(blacklist_df)} konton sparades till {BLACKLIST_CSV}")
    print(f"Svartlistning klar! {len(blacklist_df)} konton sparades till {BLACKLIST_CSV}")
else:
    logger.info("Inga misstänkta transaktioner hittades.")
    print("Inga misstänkta transaktioner hittades.")